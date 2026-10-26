# Tool của repo: bảng kiểm cho Bước 0 của skill

File này liệt kê tool mà skill trong `skills/` của repo dùng. `tools/capabilities.py` đọc bảng ở mục 2 và chạy cột "lệnh kiểm". Skill audit và build gọi script này ở Bước 0, trước bước 1 của quy trình. Gốc đường dẫn là root repo.

Bảng này kiểm tool để chạy skill. Việc cài máy mới (thư viện Python, credential Google, quyền Drive) theo `_SETUP/SETUP-MAY.md` và `python3 _SETUP/setup_doctor.py`.

## 1. Cách dùng

Mẫu Bước 0 cho skill (giữ nguyên câu, chỉ thay danh sách id):

```md
### Bước 0 — kiểm tool
Chạy "python3 tools/capabilities.py check --need '<id1,id2?>'" từ root repo. Nếu thiếu tool bắt buộc, dừng và báo tên tool. Nếu thiếu tool tuỳ chọn, dùng fallback ghi trong "tools/capabilities.md".
```

Lệnh:

| Lệnh | Việc |
|---|---|
| `python3 tools/capabilities.py check --need 'python3,jev,gemma?'` | Kiểm bộ tool của một skill. Hậu tố `?` là tool tuỳ chọn. In bảng ok/missing và fallback của tool thiếu. |
| `python3 tools/capabilities.py check --need 'jev' --json` | Như trên, in JSON cho agent đọc. |
| `python3 tools/capabilities.py list` | Liệt kê id trong bảng. |
| `python3 tools/capabilities.py key <TÊN_KEY>` | Kiểm key có trong biến môi trường hoặc `.agent-secrets/.env` (tìm từ root repo lên thư mục cha). Chỉ in "có" hoặc "thiếu". |
| `python3 tools/capabilities.py gws-auth [scope]` | Kiểm `gws` đã đăng nhập OAuth và có scope. Không in token. |

Exit code của `check`:

- 0: đủ tool bắt buộc.
- 1: thiếu ít nhất một tool bắt buộc.
- 2: id lạ, bảng lỗi hoặc sai cú pháp `--need`.

Script chạy mọi lệnh kiểm từ root repo, song song, mỗi lệnh tối đa 20 s (`--timeout`). Script che giá trị trong `.agent-secrets/.env` và chuỗi giống key trước khi in.

## 2. Bảng tool

| id | tool | dùng cho việc gì | lệnh kiểm | cách cài | fallback khi thiếu | skill dùng |
|---|---|---|---|---|---|---|
| `python3` | Python ≥ 3.9 | Chạy script `.py` của skill và `tools/` | `python3 -c "import sys; print(sys.version.split()[0]); sys.exit(sys.version_info < (3, 9))"` | `brew install python3` | Không có fallback. | Mọi skill có `scripts/*.py` |
| `requirements` | Thư viện trong `requirements.txt` | Google API, PyYAML, python-pptx, Pillow cho báo cáo và OKRs | `if python3 _SETUP/setup_doctor.py --tier B >/dev/null; then echo "đủ thư viện của requirements.txt"; else echo "thiếu thư viện: chạy python3 _SETUP/setup_doctor.py --tier B"; exit 1; fi` | `python3 _SETUP/setup_doctor.py --fix` | Không có fallback cho script cần thư viện đó. | `gtv-weekly-report`, `gtv-project-okrs` |
| `node` | Node.js ≥ 22 | Script `.mjs`: điều khiển Chrome qua CDP, critical CSS, audit deck. Node 22 có sẵn `WebSocket` và `fetch` | `node -e "console.log(process.version); process.exit(+process.versions.node.split('.')[0] >= 22 ? 0 : 1)"` | `brew install node` | Bỏ phần chạy `.mjs` và ghi giới hạn. | `wp-pagespeed`, `query-processing-diagnosis`, `semantic-media`, `blog-interactive-tools`, `wp-ui-fix`, `wp-theme-build` |
| `chrome` | Google Chrome (headless) | Chụp màn hình, đo DOM, render HTML thành ảnh | `"${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}" --version` | Cài Chrome. Máy không phải macOS: đặt `CHROME_BIN` | Đặt `CHROME_BIN` trỏ tới Chromium khác. Không có thì bỏ bước chụp, ghi giới hạn. | `wp-pagespeed`, `visual-serp-lab`, `query-processing-diagnosis`, `web-qa-gate`, `wp-theme-build`, `semantic-media`, `blog-interactive-tools`, `wp-ui-fix` |
| `playwright` | Playwright + Chromium | Xuất PDF từ deck HTML, chụp Looker | `for d in "$HOME/Library/Caches/ms-playwright"/chromium-* "$HOME/.cache/ms-playwright"/chromium-*; do [ -d "$d" ] && command -v npm >/dev/null && echo "trình duyệt $(basename "$d"), cài gói bằng npm khi chạy" && exit 0; done; exit 1` | `npm install playwright && npx playwright install chromium` | Deck HTML vẫn giao được. Xuất PDF bằng Chrome `--print-to-pdf`, hoặc ghi "chưa export". | `gtv-weekly-report`, `setup-may`, `wp-ui-fix` |
| `axe` | axe-core (`axe.min.js`) | Kiểm accessibility trên staging, nơi PSI không vào được | `for f in "$HOME"/.npm/_npx/*/node_modules/axe-core/axe.min.js; do [ -f "$f" ] && echo "$f" && exit 0; done; exit 1` | `npm install axe-core` vào thư mục tạm, hoặc chạy Lighthouse một lần bằng npx | Trang công khai: dùng hạng mục Accessibility của PSI. | `wp-pagespeed`, `web-qa-gate`, `blog-interactive-tools` |
| `ssh` | OpenSSH | Vào server site để đọc, backup, chạy WP-CLI | `ssh -V` | Có sẵn trên macOS, Linux | Không có fallback cho việc trên server. Chỉ đo từ ngoài và giao plan cho dev. | `wp-pagespeed`, `wp-security-hardening`, `wp-content-review-apply`, `image-seo-optimize`, `wp-staging-deploy`, `wp-theme-build`, `wp-paid-plugin-exit`, `blog-interactive-tools`, `wp-ui-fix`, `content-inventory-audit` |
| `wp-cli` | WP-CLI trên server | Đọc và ghi WordPress (DB, option, post) | `if command -v wp >/dev/null; then wp --version; else command -v ssh >/dev/null && echo "wp-cli chạy trên server; kiểm từng site bằng ssh <alias> wp --info"; fi` | Cài trên server theo `00-client-context/wp-server.md` | Không vào được server: chỉ đọc trang công khai và giao plan cho dev. Không ghi. | Như dòng `ssh`, `wp-staging-deploy`, `wp-theme-build`, `wp-paid-plugin-exit`, `blog-interactive-tools`, `wp-ui-fix`, `content-inventory-audit` |
| `cwebp` | libwebp `cwebp` | Đổi ảnh sang WebP | `cwebp -version` | `brew install webp` | Pillow lưu WebP. | `wp-pagespeed`, `image-seo-optimize` |
| `pngquant` | pngquant | Nén PNG có mất mát | `pngquant --version` | `brew install pngquant` | Chuyển ảnh sang WebP thay vì nén PNG. | `wp-pagespeed` |
| `ffmpeg` | FFmpeg | Cắt clip, tách khung hình, ghép video | `ffmpeg -version` | ok · ffmpeg 9.0.1 | Bỏ phần video, ghi giới hạn. Cài `brew install ffmpeg`. | `semantic-media` |
| `pillow` | Pillow (Python) | Xử lý ảnh, so ảnh, chụp vùng sheet | `python3 -c "import PIL; print('Pillow', PIL.__version__)"` | `python3 -m pip install Pillow` | Bỏ xử lý ảnh, ghi giới hạn. seo-onpage: `serp_pixel.py` tự đo bằng bảng `scripts/arial_widths.json`. | `visual-serp-lab`, `wp-pagespeed`, `gtv-weekly-report`, `seo-onpage`, `wp-theme-build`, `semantic-media`, `wp-ui-fix` |
| `fonttools` | fontTools + brotli (Python) | Cắt font, dựng font dự phòng có metric khớp | `python3 -c "import fontTools, brotli; print('fontTools', fontTools.version)"` | `python3 -m pip install fonttools brotli` | Bỏ `fallback_faces.py` và `fa_subset/`, ghi giới hạn. | `wp-pagespeed` |
| `lighthouse` | Lighthouse (npm, cache npx) | Mô phỏng PSI trên máy cho lỗi chỉ PSI thấy | `for d in "$HOME"/.npm/_npx/*/node_modules/lighthouse; do [ -d "$d" ] && echo "lighthouse: $d" && exit 0; done; exit 1` | `npx -y lighthouse --version` (tải vào cache npx) | Dùng PSI thật, ghi giới hạn. | `wp-pagespeed` |
| `numpy` | NumPy | Tính cosine, AUC, ma trận cho lớp model | `python3 -c "import numpy; print('numpy', numpy.__version__)"` | `python3 -m pip install numpy` | Chạy script bằng venv EmbeddingGemma (có numpy). | `model-calibration`, `site-vector-index`, `retrieval-lab`, `topical-focus`, `content-quality-lab`, `link-relevance`, `visual-serp-lab`, `serp-clustering`, `geo-fanout-research`, `content-refresh`, `hreflang-planner`, `semantic-content-audit` |
| `bs4` | beautifulsoup4 | Parse HTML trang | `python3 -c "import bs4; print('beautifulsoup4', bs4.__version__)"` | `python3 -m pip install beautifulsoup4` | Parse bằng `python3 -E` của hệ thống nếu venv thiếu bs4, embed bằng venv. | `site-vector-index`, `visual-serp-lab`, `semantic-content-audit`, `semantic-media` |
| `jev` | Jev 1.14 qua OpenRouter (`tools/ai-assist/jev.py`) | Phân loại, chấm điểm, QA chữ và ảnh giao diện. Chỉ nhận nội dung web công khai | `test -f tools/ai-assist/jev.py && python3 tools/capabilities.py key OPENROUTER_JEV_API_KEY` | Đặt `OPENROUTER_JEV_API_KEY` trong `.agent-secrets/.env` (`tools/ai-assist/README.md` mục 5) | Claude gán nhãn mẫu nhỏ và ghi giới hạn "không có Jev". Không thay bằng model khác. | `content-quality-lab`, `link-relevance`, `visual-serp-lab`, `geo-answer-lab`, `topical-focus`, `model-calibration`, `wp-pagespeed`, `wp-security-hardening`, `wp-content-review-apply`, `technical-seo-audit` (nhánh GSC), `internal-linking`, `seo-drift-tracker`, `semantic-content-audit`, `wp-ui-fix` |
| `glm` | GLM Flash qua OpenRouter (`tools/ai-assist/glm.py`) | Chỉ trích câu nguyên văn khi Jev không làm được | `test -f tools/ai-assist/glm.py && python3 tools/capabilities.py key OPENROUTER_API_KEY` | Đặt `OPENROUTER_API_KEY` trong `.agent-secrets/.env` | Claude trích câu nguyên văn trực tiếp từ nguồn. | `geo-answer-lab` |
| `gemma` | EmbeddingGemma 2 local (`~/.venvs/embeddinggemma`) | Embedding, cosine, gom cụm, so ảnh với chữ. Dữ liệu không rời máy | `"$HOME/.venvs/embeddinggemma/bin/python" -c "import sentence_transformers, torch; print('sentence-transformers', sentence_transformers.__version__, 'mps', torch.backends.mps.is_available())" && test -d "${HF_HOME:-$HOME/.cache/huggingface}/hub/models--google--embeddinggemma-2"` | Tạo venv và tải model theo `tools/ai-assist/README.md` mục 5 | Dừng phần cần embedding và báo người vận hành. Không gọi API embedding bên ngoài thay thế. | `site-vector-index`, `retrieval-lab`, `topical-focus`, `content-quality-lab`, `link-relevance`, `visual-serp-lab`, `model-calibration`, `wp-pagespeed`, `wp-security-hardening`, `serp-clustering`, `keyword-topic-url-mapping`, `query-processing-diagnosis`, `geo-fanout-research`, `geo-content-optimization`, `content-refresh`, `hreflang-planner`, `semantic-media` |
| `screaming-frog` | Screaming Frog SEO Spider (CLI `--headless`) | Crawl toàn site, xuất tab và report | `defaults read "/Applications/Screaming Frog SEO Spider.app/Contents/Info" CFBundleShortVersionString && test -s "$HOME/.ScreamingFrogSEOSpider/licence.txt" && echo "licence: có"` | Cài app, nhập licence trong GUI một lần | Crawl bằng sitemap + script, hoặc Path A/C của `technical-seo-audit`. | `technical-seo-audit` (Path B), `site-migration-checklist`, `hreflang-planner`, `internal-linking` |
| `gws` | Google Workspace CLI (`gws`) | Đọc Sheet, Drive, GSC bằng OAuth của người vận hành | `gws --version >/dev/null && python3 tools/capabilities.py gws-auth` | `npm install -g @googleworkspace/cli`, rồi `gws auth login` | Dùng service account (`gcp-sa`). | `tools/gsc/gsc.sh`, `query-processing-diagnosis`, `seo-logfile-analysis` |
| `gsc` | `tools/gsc/gsc.sh` (GSC API qua OAuth của `gws`) | Search Analytics, URL Inspection, sitemap | `test -x tools/gsc/gsc.sh && python3 tools/capabilities.py gws-auth webmasters.readonly` | Đăng nhập `gws` có scope `webmasters.readonly`; property phải share cho tài khoản đó | Xin người vận hành export CSV từ GSC. Không gửi dữ liệu GSC vào Jev. | `technical-seo-audit`, `wp-pagespeed`, `link-relevance`, `retrieval-lab`, `topical-focus`, `content-refresh`, `query-processing-diagnosis`, `blog-interactive-tools` |
| `gcp-sa` | Service account Google của người vận hành | Đọc workbook báo cáo và OKRs | `if python3 _SETUP/setup_doctor.py --tier C >/dev/null; then echo "credential Google: đạt"; else echo "credential Google: chưa đạt, xem python3 _SETUP/setup_doctor.py --tier C"; exit 1; fi` | `_SETUP/HUONG-DAN-GOOGLE-CREDENTIAL.md` | Dùng `gws`. Workbook chưa share cho service account thì xin share. | `gtv-weekly-report`, `gtv-project-okrs` |
| `uv` | uv / uvx | Chạy MCP `mcp-gsc`, `google-sheets`, `ga4-mcp` trong `.mcp.json` | `uv --version` | `brew install uv` | Dùng `gws` và `tools/gsc/gsc.sh`. | MCP trong `.mcp.json` |
| `openrouter` | OpenRouter chat (`OPENROUTER_API_KEY`) | Thu câu trả lời AI (Perplexity Sonar, Gemini…) cho bộ prompt GEO | `python3 tools/capabilities.py key OPENROUTER_API_KEY` | Đặt key trong `.agent-secrets/.env` | Thu câu trả lời bằng tay trên từng engine, ghi ngày giờ. Không dùng để tạo ảnh. | `geo-answer-lab` (`collect.py`), `geo-tracking-prompt-selection` (bước đo qua `collect.py`) |
| `firecrawl` | Firecrawl (MCP + API key) | Scrape, crawl, search trang web | `python3 tools/capabilities.py key FIRECRAWL_API_KEY` | Đặt key trong `.agent-secrets/.env`; MCP theo `config/mcp.json.example` | Tavily, rồi `curl` + bs4 cho trang tĩnh, rồi web search của runtime. | `geo-fanout-research`, `geo-content-optimization`, `seo-onpage`, `technical-seo-audit` (Path C), `query-processing-diagnosis`, `schema-markup-generator` |
| `tavily` | Tavily (MCP + API key) | Search, extract, crawl | `python3 tools/capabilities.py key TAVILY_API_KEY` | Đặt key trong `.agent-secrets/.env` | Firecrawl search hoặc web search của runtime. | `geo-fanout-research` |
| `pagespeed-api` | PageSpeed Insights API (`PAGESPEED_API_KEY`) | Đo PSI 3 lượt, CWV, Accessibility | `python3 tools/capabilities.py key PAGESPEED_API_KEY` | Tạo key PSI trên Google Cloud, đặt trong `.agent-secrets/.env` | Gọi PSI không key (ít lượt hơn), hoặc Lighthouse local cho staging. Ghi rõ số đo không phải PSI. | `wp-pagespeed`, `technical-seo-audit`, `site-migration-checklist` |
| `dataforseo` | DataForSEO API | SERP, volume keyword, local grid | `python3 tools/capabilities.py key DATAFORSEO_LOGIN DATAFORSEO_PASSWORD` | Đặt 2 key trong `.agent-secrets/.env` | SERP qua Firecrawl search; volume từ export người vận hành gửi. | `map-pack-intelligence`, `serp-clustering`, `keyword-topic-url-mapping`, `traffic-plan`, `local-seo-audit`, `backlink-research` |
| `ahrefs` | Ahrefs (MCP `@ahrefs/mcp` hoặc connector của runtime) | Backlink, keyword, số trích dẫn AI | `python3 tools/capabilities.py key AHREFS_API_KEY` | Đặt key trong `.agent-secrets/.env`; MCP theo `config/mcp.json.example` | Script không thấy connector Ahrefs của runtime. Agent gọi `subscription-info-limits-and-usage`; nếu gọi được thì dùng connector. Không có connector thì dùng export CSV người vận hành gửi. | `backlink-research`, `backlink-plan`, `textlink-analyzer`, `link-relevance` (nhánh backlink), `geo-tracking-prompt-selection`, `keyword-topic-url-mapping`, `traffic-plan`, `geo-content-optimization`, `content-refresh` |
| `curl` | curl | Lấy header, mã HTTP, trang công khai | `curl --version` | Có sẵn trên macOS, Linux | `python3` + `urllib`. | `query-processing-diagnosis`, `seo-drift-tracker`, `wp-security-hardening` |
| `git` | Git | Đồng bộ repo với GitHub (`tools/project_sync.py`) | `git --version` | `brew install git` | Không đồng bộ được. Báo người vận hành. | `tools/project_sync.py` |

## 3. Luật tool cần nhớ

- Jev chỉ nhận nội dung web công khai. Không gửi GSC, hợp đồng, email của khách vào Jev. Jev không đếm và không viết content. GLM Flash chỉ trích câu nguyên văn.
- Repo này không tạo ảnh AI. Không gọi OpenRouter để tạo ảnh.
- MCP Firecrawl, Tavily, Ahrefs là capability của runtime. Script không kiểm được MCP. Agent kiểm bằng danh sách tool của phiên: có `firecrawl_scrape`, `tavily_search` là có MCP. Key trong `.agent-secrets/.env` chỉ chứng minh script gọi được API.
- Lệnh `npx playwright` không có `--no` sẽ tự tải bản mới nhất. Không chạy lệnh đó chỉ để kiểm.

## 4. Thêm hoặc sửa một dòng

1. Đặt id dạng kebab-case, chữ thường. Không đổi id đã có, vì skill gọi id trong Bước 0.
2. Viết lệnh kiểm chỉ đọc, chạy dưới 20 s, không cần mạng nếu được. Đặt lệnh trong một cặp dấu `` ` ``.
3. Viết dấu `|` trong lệnh thành `\|`.
4. Kiểm key bằng `python3 tools/capabilities.py key <TÊN>`. Không in giá trị key.
5. Không ghi tên máy, tài khoản hay dữ liệu khách vào bảng này.
6. Chạy test: `python3 -m unittest discover -s tools/tests -p test_capabilities.py`.

## Lịch sử

- 2026-10-19: tạo mới, 29 id. Skill audit và build thêm Bước 0 theo mục 1.
