#!/bin/bash
# php_tai.sh (wp-host-optimize): phân loại access log OpenLiteSpeed theo nhóm actor × loại endpoint, đếm request PHP và PHP-giây.
# Chỉ đọc. Chạy trên server, in dòng thô ra stdout; tổng hợp trên máy bằng tong_hop_php_tai.py.
# Dùng: ssh <host> "WSTART='YYYY-MM-DD HH:MM' [WEND='…'] VHS='<vhost> …' [NOIBO='<ip> …'] [LOGD=/www/wwwlogs] bash -s" < php_tai.sh > php_tai.txt
#   VHS: tên vhost theo tên file log. LOG_GLOB mặc định '%s_ols.access_log*' (aaPanel).
#   NOIBO: IP văn phòng và IP khác của agent. IP của server (hostname -I), IP của phiên SSH đang chạy script, 127.x, ::1 tự tính là nội bộ.
#   Lỗi đã gặp 27/10/2026: thiếu IP của máy agent, lượt đo của lane bị tính là IP quét, chiếm 92% PHP-giây bên ngoài.
# Cần gawk trên server. Log cần %D (micro giây, không ngoặc) ngay sau "User-Agent" và cột cache trong ngoặc kép:
#   %{X-Forwarded-For}i %h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i" %D "%{X-LiteSpeed-Cache}o"
#   Vhost thiếu 2 cột này vẫn chạy, nhưng số PHP là trần trên và PHP-giây = 0 (dòng G có per=noD).
# Nguồn: đo tải site agency mẫu 16–26/10/2026 (mốc trước và sau Đợt 1, 48 giờ).
[ -n "${WSTART:-}" ] && [ -n "${VHS:-}" ] || { echo "thiếu WSTART hoặc VHS" >&2; exit 2; }
command -v gawk >/dev/null || { echo "server thiếu gawk" >&2; exit 2; }
WEND="${WEND:-$(date '+%Y-%m-%d %H:%M')}"
LOGD="${LOGD:-/www/wwwlogs}"
LOG_GLOB="${LOG_GLOB:-%s_ols.access_log*}"
NOIBO="${NOIBO:-} $(hostname -I 2>/dev/null) ${SSH_CLIENT%% *}"
IO="nice -n 19"; command -v ionice >/dev/null && IO="$IO ionice -c3"
echo "#RUN|$(date '+%Y-%m-%d %H:%M:%S %z')|$WSTART|$WEND"

read -r -d '' COMMON <<'EOF'
function parse(   n,P,X,R,S,nq) {
  if (!match($0, /\[[0-9][0-9]\/[A-Z][a-z][a-z]\/[0-9][0-9][0-9][0-9]:[0-9][0-9]:[0-9][0-9]:[0-9][0-9]/)) return 0
  ts=substr($0,RSTART+1,RLENGTH-1); pre=substr($0,1,RSTART-1)
  dd=substr(ts,1,2); mo=MON[substr(ts,4,3)]; yy=substr(ts,8,4); hh=substr(ts,13,2); mi=substr(ts,16,2); ss=substr(ts,19,2)
  day=yy"-"mo"-"dd; minute=day" "hh":"mi
  if (minute < WSTART || minute >= WEND) return 0
  n=split(pre,P," "); ip=P[n-2]; xff=(n>=4)?P[1]:"-"; gsub(/'/,"",xff)
  if (xff!="-" && xff!="") { split(xff,X,","); ip=X[1] }
  nq=split($0,q,"\"")
  split(q[2],R," "); meth=R[1]; uri=R[2]
  split(q[3],S," "); st=S[1]
  ua=(nq>=6)?q[6]:"-"
  D=-1; cache="na"
  if (nq>=8 && q[7] ~ /^ *[0-9]+ *$/) { D=q[7]+0; cache=q[8]; if (cache=="") cache="-" }
  qpos=index(uri,"?"); path=(qpos?substr(uri,1,qpos-1):uri); qs=(qpos?substr(uri,qpos+1):"")
  lpath=tolower(path)
  isstatic=(lpath ~ /\.(css|js|mjs|map|png|jpe?g|gif|webp|avif|svg|ico|bmp|tiff?|woff2?|ttf|otf|eot|mp4|webm|mov|m4v|mp3|wav|ogg|pdf|zip|rar|7z|gz|tgz|bz2|csv|docx?|xlsx?|pptx?|swf|apk|exe|dmg|psd|eps|heic)$/)
  notfound=(st=="404" || st=="410")
  return 1
}
function exploit() {
  if (lpath ~ /guest\.vary\.php$/) return 0
  if (lpath ~ /(^|\/)\.[^\/]/ && lpath !~ /^\/\.well-known\//) return 1
  if (lpath ~ /xmlrpc\.php|wp-config|eval-stdin|phpunit|\/vendor\/|\/cgi-bin\/|phpmyadmin|\/pma\/|adminer|\/server-status|\/actuator|\/boaform|\/hnap1|\/owa\/|autodiscover|\/wp-admin\/(install|setup-config|maint)|\.(aspx?|jsp|cgi|env|sql|bak|old|swp|tar|rar|7z)$|\/wp-includes\/.+\.php|\/wp-content\/(plugins|themes|uploads)\/.+\.php|wp-file-manager|filemanager/) return 1
  if (qs ~ /(^|&)author=[0-9]/ || lpath ~ /^\/wp-json\/wp\/v2\/users|^\/wp-json\/batch/ || qs ~ /rest_route=\/(wp\/v2\/users|batch)/) return 1
  if (lpath ~ /\.php$/ && lpath !~ /^\/(index|wp-cron|wp-login|wp-comments-post|wp-signup|wp-activate|wp-trackback)\.php$/ && lpath !~ /^\/wp-admin\//) return 1
  return 0
}
function noibo() { return ((ip in NB) || ip ~ /^127\./ || ip=="::1") }
function goodbot(u) { return (u ~ /Googlebot|Google-InspectionTool|GoogleOther|Storebot-Google|AdsBot-Google|Mediapartners-Google|bingbot|GPTBot|OAI-SearchBot|ChatGPT|ClaudeBot|Claude-User|Claude-SearchBot|PerplexityBot|Perplexity-User|Applebot|AhrefsBot|AhrefsSiteAudit|coccocbot|facebookexternalhit|Zalo|YandexBot|meta-external|Amazonbot|DuckDuckBot|SemrushBot|MJ12bot|DotBot|PetalBot|Bytespider|BLEXBot|DataForSeoBot|WP Rocket|Lighthouse|Twitterbot|LinkedInBot|TelegramBot/) }
BEGIN{ split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec",mn," "); for(i=1;i<=12;i++) MON[mn[i]]=sprintf("%02d",i)
  nn=split(NOIBO,nbi," "); for(i=1;i<=nn;i++) NB[nbi[i]]=1 }
EOF

read -r -d '' PASS1 <<'EOF'
{ if (!parse()) next
  if (noibo() || goodbot(ua)) next
  if (!isstatic) { NT[ip]++; if (notfound) N4[ip]++ }
  if (exploit()) EX[ip]++
}
END{ for (i in NT) if ((N4[i]>=20 && N4[i]/NT[i]>=0.5) || EX[i]>=2) printf "%s ", i }
EOF

read -r -d '' PASS2 <<'EOF'
function actor(   u) {
  u=ua
  if (u ~ /WP Rocket\/Preload|litespeed_crawler|lscache_runner|LiteSpeed-Crawler|lscache_walker/) return "preload"
  if (noibo()) return "noi-bo"
  if (u ~ /Chrome-Lighthouse|Google-PageSpeed|PTST|GTmetrix/) return "psi-lighthouse"
  if (u ~ /Googlebot|Google-InspectionTool|GoogleOther|Storebot-Google|AdsBot-Google|Mediapartners-Google|APIs-Google|FeedFetcher-Google|Google-Site-Verification|Google-Safety|Google-Read-Aloud|bingbot|BingPreview|msnbot|adidxbot|MicrosoftPreview/) return "google-bing"
  if (u ~ /GPTBot|OAI-SearchBot|ChatGPT|ClaudeBot|Claude-User|Claude-SearchBot|anthropic-ai|PerplexityBot|Perplexity-User|Applebot|Google-Extended|Google-CloudVertexBot/) return "ai-giu"
  if (u ~ /AhrefsBot|AhrefsSiteAudit/) return "ahrefs"
  if (u ~ /GoogleImageProxy|ggpht\.com|YahooMailProxy|OneOutlook|Outlook-iOS|Microsoft Office|Thunderbird|Superhuman|FrontApp|Mailspring/) return "mail-proxy"
  if (ip in BAD) return "scanner-ip"
  if (u ~ /meta-externalagent|meta-externalfetcher|FacebookBot|Amazonbot|CCBot|DuckAssistBot|MistralAI|YouBot|Diffbot|cohere-ai|ImagesiftBot|Timpibot|AI2Bot|Ai2Bot|PanguBot|Kangaroo Bot|iaskspider|Brightbot|img2dataset|TikTokSpider|QualifiedBot|Novellum|archive\.org_bot|ia_archiver|Bravebot|PhindBot|Andibot|Cotoyogi|LinerBot|SBIntuitionsBot/) return "ai-khac"
  if (u ~ /coccocbot|DuckDuckBot|YandexBot|YandexImages|YandexMobileBot|YandexRenderResources|Baiduspider|Sogou|360Spider|SeznamBot|Yeti\/|MojeekBot|Qwantbot|Qwantify|Exabot/) return "se-khac"
  if (u ~ /SemrushBot|SiteAuditBot|SplitSignalBot|MJ12bot|DotBot|PetalBot|Bytespider|BLEXBot|DataForSeoBot|serpstatbot|SeekportBot|Barkrowler|MegaIndex|SERankingBacklinksBot|SEOkicks|linkdexbot|rogerbot|dataprovider|ZoominfoBot|Screaming Frog|SEOlyticsCrawler|Sitebulb|spbot|BacklinkCrawler|LinkpadBot|Seobility|woorank|Siteimprove|netEstate|GeedoBot|keys-so-bot|Majestic|Pandalytics|SurdotlyBot|Turnitin|AwarioBot|BrandVerity|Mail\.RU_Bot|SemanticScholarBot|MauiBot|Cliqzbot|Owler|Orbbot|SenutoBot|MTRobot|startmebot|Proximic|GrapeshotCrawler|Amzn-SearchBot|wpbot/) return "seo-khac"
  if (u ~ /facebookexternalhit|facebookcatalog|Zalo|Twitterbot|LinkedInBot|TelegramBot|Slackbot|Discordbot|WhatsApp|Skype|Pinterest|redditbot|Embedly|vkShare|Viber|Iframely|Mastodon/) return "social"
  if (u ~ /UptimeRobot|Pingdom|StatusCake|Site24x7|Better Uptime|Uptime-Kuma|Jetpack|WordPress\.com|NewRelic|Datadog|Wordfence|ManageWP|MainWP|Let's Encrypt|letsencrypt|Cloudflare-|Hetrix|Freshping/) return "monitor"
  if (u == "-" || u == "" || u ~ /^(curl|Wget|python|Python|Go-http-client|okhttp|Java\/|libwww|lwp-|axios|node-fetch|undici|node|PHP\/|GuzzleHttp|Ruby|Scrapy|httpx|aiohttp|HTTPie|Apache-HttpClient|fasthttp|colly|Faraday|rest-client|PostmanRuntime|Dalvik|WinHttp|Microsoft-WebDAV|masscan|zgrab|Nmap|nuclei|Nikto|sqlmap|WPScan|Fuzz|Mozlila|Mozila)/ || u ~ /zgrab|Nuclei|nikto|sqlmap|wpscan|masscan|CensysInspect|Odin|InternetMeasurement|Palo Alto|Expanse|l9explore|l9tcpid|ZmEu/) return "script"
  if (u ~ /HeadlessChrome|PhantomJS|Puppeteer|Playwright|Selenium|Electron/) return "headless"
  if (u ~ /WordPress\/[0-9]/) return "wp-loopback"
  if (u ~ /[Bb]ot|[Cc]rawl|[Ss]pider|[Ss]lurp|[Ff]etch|[Ss]can|[Cc]hecker|[Pp]review|[Vv]alidator|https?:\/\//) return "bot-khac"
  if (u ~ /Chrome\/[0-9]+\.[0-9]+ Safari/ || u ~ /MSIE |Trident\//) return "ua-cu-gia"
  if (match(u,/Chrome\/[0-9]+/) && substr(u,RSTART+7,RLENGTH-7)+0 < 110) return "ua-cu-gia"
  if (match(u,/Firefox\/[0-9]+/) && substr(u,RSTART+8,RLENGTH-8)+0 < 100) return "ua-cu-gia"
  return "nguoi-dung"
}
function endpoint() {
  if (uri ~ /doing_wp_cron/ || lpath=="/wp-cron.php") return "wpcron"
  if (lpath ~ /guest\.vary\.php$/) return "guest-vary"
  if (lpath=="/wp-admin/admin-ajax.php") return "admin-ajax"
  if (lpath ~ /^\/(wp-login|wp-signup|wp-register|wp-activate)\.php/ || qs ~ /(^|&)action=register/ || lpath ~ /\/(my-account|tai-khoan|dang-ky|dang-nhap|register|registration|login|signup)(\/|$)/) return "login-dangky"
  if (exploit()) return "khai-thac"
  if (lpath ~ /^\/wp-admin(\/|$)/) return "wp-admin"
  if (lpath ~ /^\/wp-json(\/|$)/ || qs ~ /rest_route=/) return "rest-api"
  if (isstatic) return (notfound ? "tinh-404" : "tinh")
  if (lpath ~ /^\/robots\.txt$|sitemap[^\/]*\.xml$|\.xsl$/) return "robots-sitemap"
  if (lpath ~ /\/feed\/?$|\/rss\/?$|\/atom\/?$/) return "feed"
  if (qs ~ /(^|&)s=/) return "tim-kiem"
  if (lpath ~ /\/page\/[0-9]+\/?$/ || qs ~ /(^|&)paged?=/) return "phan-trang"
  if (notfound) return "trang-404"
  return "trang"
}
function qkey(s) {
  if (s ~ /srsltid=/) return "srsltid"
  if (s ~ /(^|&)fbclid=/) return "fbclid"
  if (s ~ /(^|&)(gclid|gbraid|wbraid|gad_source|gad_campaignid)=/) return "gclid-gad"
  if (s ~ /(^|&)utm_[a-z]+=/) return "utm"
  if (s ~ /(^|&)(zarsrc|_ga|_gl|msclkid|ttclid|mc_cid|mc_eid|dclid)=/) return "tracking-khac"
  if (s ~ /(^|&)s=/) return "s-tim-kiem"
  if (s ~ /add-to-cart|wc-ajax|add_to_wishlist/) return "woo"
  if (s ~ /(^|&)(nc|rd[0-9]*|nocache|cb)=/) return "nc-lane"
  if (s ~ /doing_wp_cron/) return "wpcron"
  if (s ~ /(^|&)(p|page_id|cat|tag|attachment_id)=/) return "p-id"
  if (s ~ /(^|&)(paged|page)=/) return "paged"
  if (s ~ /replytocom/) return "replytocom"
  if (s ~ /(^|&)(amp|noamp)(=|&|$)/) return "amp"
  if (s ~ /(^|&)lang=/) return "lang"
  if (s ~ /(^|&)(ver|v)=/) return "ver"
  if (s ~ /(^|&)q=/) return "q-tim-kiem"
  if (s ~ /(^|&)author=/) return "author"
  if (s ~ /rest_route/) return "rest_route"
  if (s ~ /(^|&)(preview|preview_id|elementor-preview|elementor_library)/) return "preview"
  if (s ~ /(^|&)(orderby|order|filter_|min_price|max_price|product_cat)/) return "loc-sap-xep"
  if (s ~ /(^|&)action=/) return "action"
  return "khac"
}
BEGIN{ nb=split(BADS,bb," "); for(i=1;i<=nb;i++) BAD[bb[i]]=1 }
{ if (!parse()) next
  a=actor(); e=endpoint(); hasD=(D>=0)
  if (cache=="") cache="-"
  if (hasD) {
    if (cache=="miss") php=1
    else if (cache ~ /^hit/) php=0
    else if (st=="403") php=0
    else if (e=="wpcron" || e=="guest-vary" || e=="admin-ajax") php=1
    else php=(D>=100000 && !(isstatic && st ~ /^(200|206|304)$/))
  } else php=(!isstatic && st !~ /^(403|400|408|444|499|304)$/) || (isstatic && notfound && lpath !~ /^\/wp-content\/uploads\//)
  per=(hasD?"D":"noD")
  k=per"|"day"|"a"|"e
  T[k]++; if(php){PP[k]++; if(hasD) PS[k]+=D/1e6}
  if(cache ~ /^hit/)HH[k]++; else if(cache=="miss")MM[k]++
  if(notfound)F4[k]++; if(st=="403")F3[k]++; if(st ~ /^5/)F5[k]++
  if(meth=="POST")PO[k]++
  if (php) { hk=day" "hh"|"a"|"e; HP[hk]++; if(hasD) HS[hk]+=D/1e6 }
  if (php && hasD) {
    mk=minute"|"a"|"e; MP[mk]++; MS[mk]+=D/1e6
    if (!(minute in EP)) EP[minute]=mktime(yy" "mo" "dd" "hh" "mi" 00")
    s0=EP[minute]+ss; s1=s0+D/1e6
    for (b=s0; b<=int(s1) && b-s0<120; b++) { ov=((b+1<s1)?b+1:s1)-b; if (ov>0) { OCC[b]+=ov; if (a!="noi-bo" && a!="psi-lighthouse" && e!="wpcron") OCX[b]+=ov } }
  }
  if (qs!="" && !isstatic) { qk=qkey(qs); QK[per"|"qk"|"cache"|"php"|"(a=="noi-bo"?"noi-bo":"ngoai")]++; if (qk=="khac" && a!="noi-bo") { split(qs,qa,"[=&]"); QN[substr(qa[1],1,30)]++ } }
  if (a!="noi-bo") { ik=ip"|"a; IT[ik]++; if(php){IPP[ik]++; if(hasD) ISS[ik]+=D/1e6}; if(notfound)I4[ik]++ }
  if (a!="noi-bo" && a!="nguoi-dung") { uk=a"|"substr(ua,1,140); UT[uk]++; if(php)UP[uk]++ }
  if (php && a!="noi-bo") { pk=per"|"a"|"e"|"substr(path,1,80); PT[pk]++; if(hasD) PTS[pk]+=D/1e6 }
  if (e ~ /^trang|phan-trang|feed|tim-kiem/ && meth=="GET" && hasD && a!="noi-bo" && a!="psi-lighthouse") CR[a"|"cache]++
}
END{
  V=VH
  for (k in T) print "G|"V"|"k"|"T[k]"|"PP[k]+0"|"sprintf("%.1f",PS[k])"|"HH[k]+0"|"MM[k]+0"|"F4[k]+0"|"F3[k]+0"|"F5[k]+0"|"PO[k]+0
  for (k in HP) print "H|"V"|"k"|"HP[k]"|"sprintf("%.1f",HS[k])
  for (k in MP) print "M|"V"|"k"|"MP[k]"|"sprintf("%.2f",MS[k])
  for (b in OCC) { m=strftime("%Y-%m-%d %H:%M",b); if (OCC[b]>CM[m]) CM[m]=OCC[b]; if (OCX[b]>CX[m]) CX[m]=OCX[b]; CS[m]+=OCC[b]; CXS[m]+=OCX[b]; if (OCC[b]>=8 || OCX[b]>=6) print "S|"V"|"strftime("%Y-%m-%d %H:%M:%S",b)"|"sprintf("%.1f|%.1f",OCC[b],OCX[b]) }
  for (m in CM) print "C|"V"|"m"|"sprintf("%.2f|%.2f|%.3f|%.3f",CM[m],CX[m]+0,CS[m]/60,CXS[m]/60)
  for (k in QK) print "Q|"V"|"k"|"QK[k]
  for (k in QN) if (QN[k]>=10) print "QN|"V"|"k"|"QN[k]
  for (k in IT) if (IT[k]>=200 || IPP[k]>=20 || I4[k]>=20) print "I|"V"|"k"|"IT[k]"|"IPP[k]+0"|"sprintf("%.1f",ISS[k])"|"I4[k]+0
  for (k in UT) if (UT[k]>=20 || UP[k]>=10) print "U|"V"|"k"|"UT[k]"|"UP[k]+0
  for (k in PT) if (PT[k]>=15) print "P|"V"|"k"|"PT[k]"|"sprintf("%.1f",PTS[k])
  for (k in CR) print "CR|"V"|"k"|"CR[k]
}
EOF

for VH in $VHS; do
  FILES=$(find "$LOGD" -maxdepth 1 -name "$(printf "$LOG_GLOB" "$VH")" -newermt "$WSTART" | sort)
  echo "#FILES|$VH|$(echo "$FILES" | grep -c .)|$(cat $FILES 2>/dev/null | wc -c)"
  BADS=$(for f in $FILES; do gzip -dcf "$f"; done | $IO gawk -v WSTART="$WSTART" -v WEND="$WEND" -v NOIBO="$NOIBO" "$COMMON
$PASS1")
  echo "#BADN|$VH|$(echo $BADS | wc -w)"
  for f in $FILES; do gzip -dcf "$f"; done | $IO gawk -v VH="$VH" -v BADS="$BADS" -v WSTART="$WSTART" -v WEND="$WEND" -v NOIBO="$NOIBO" "$COMMON
$PASS2"
done
echo "#END|$(date '+%Y-%m-%d %H:%M:%S')"
