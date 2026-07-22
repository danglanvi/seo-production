// pdf2png.swift — render PDF → PNG bằng PDFKit (có sẵn macOS, không cần poppler).
// Dùng: swift pdf2png.swift <in.pdf> <outdir> [scale=2.0] [prefix=page]
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else { print("usage: swift pdf2png.swift <in.pdf> <outdir> [scale] [prefix]"); exit(1) }
let pdfPath = args[1]
let outDir = args[2]
let scale: CGFloat = args.count > 3 ? CGFloat(Double(args[3]) ?? 2.0) : 2.0
let prefix = args.count > 4 ? args[4] : "page"

guard let doc = PDFDocument(url: URL(fileURLWithPath: pdfPath)) else { print("ERROR: cannot open PDF"); exit(1) }
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)
for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let bounds = page.bounds(for: .mediaBox)
    let size = CGSize(width: bounds.width * scale, height: bounds.height * scale)
    let img = NSImage(size: size)
    img.lockFocus()
    NSColor.white.setFill()
    NSRect(origin: .zero, size: size).fill()
    let ctx = NSGraphicsContext.current!.cgContext
    ctx.saveGState(); ctx.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: ctx)
    ctx.restoreGState()
    img.unlockFocus()
    guard let tiff = img.tiffRepresentation, let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:]) else { continue }
    let out = doc.pageCount == 1 ? "\(outDir)/\(prefix).png" : String(format: "%@/%@-%02d.png", outDir, prefix, i + 1)
    try? png.write(to: URL(fileURLWithPath: out))
    print("wrote \(out)")
}
