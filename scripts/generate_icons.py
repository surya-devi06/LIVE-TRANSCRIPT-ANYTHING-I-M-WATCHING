"""Utility script to generate professional application icons for Live Transcript."""

from pathlib import Path
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QApplication


def render_icon_image(size: int) -> QImage:
    """Render a modern Live Transcript app icon at the specified resolution."""
    image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    scale = size / 256.0

    # 1. Background rounded rectangle with gradient
    bg_path = QPainterPath()
    bg_rect = QRectF(8 * scale, 8 * scale, 240 * scale, 240 * scale)
    corner_radius = 48 * scale
    bg_path.addRoundedRect(bg_rect, corner_radius, corner_radius)

    bg_grad = QLinearGradient(0, 0, size, size)
    bg_grad.setColorAt(0.0, QColor("#0F172A"))  # Dark Slate
    bg_grad.setColorAt(1.0, QColor("#1E293B"))  # Navy Slate
    painter.fillPath(bg_path, QBrush(bg_grad))

    # Border glow
    border_pen = QPen(QColor("#38BDF8"), max(1.5, 3.5 * scale))
    painter.strokePath(bg_path, border_pen)

    # 2. Soundwave / Audio bars
    bar_color = QColor("#38BDF8")  # Cyan
    accent_color = QColor("#0284C7")  # Deep Sky Blue
    bars = [
        (64 * scale, 120 * scale, 16 * scale, 48 * scale),
        (92 * scale, 90 * scale, 16 * scale, 96 * scale),
        (120 * scale, 65 * scale, 16 * scale, 136 * scale),
        (148 * scale, 85 * scale, 16 * scale, 104 * scale),
        (176 * scale, 115 * scale, 16 * scale, 56 * scale),
    ]

    for idx, (bx, by, bw, bh) in enumerate(bars):
        bar_path = QPainterPath()
        bar_rect = QRectF(bx, by, bw, bh)
        bar_path.addRoundedRect(bar_rect, bw / 2, bw / 2)
        grad = QLinearGradient(bx, by, bx, by + bh)
        grad.setColorAt(0.0, bar_color)
        grad.setColorAt(1.0, accent_color)
        painter.fillPath(bar_path, QBrush(grad))

    # 3. Live badge dot (pulsing indicator in bottom right)
    dot_x = 195 * scale
    dot_y = 195 * scale
    dot_r = 14 * scale
    dot_grad = QLinearGradient(dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r)
    dot_grad.setColorAt(0.0, QColor("#34D399"))  # Emerald Green
    dot_grad.setColorAt(1.0, QColor("#059669"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(dot_grad))
    painter.drawEllipse(QPointF(dot_x, dot_y), dot_r, dot_r)

    # White inner dot highlight
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawEllipse(QPointF(dot_x - 3 * scale, dot_y - 3 * scale), 4 * scale, 4 * scale)

    painter.end()
    return image


def main() -> None:
    # Need a minimal QApplication for Qt rendering
    app = QApplication.instance() or QApplication([])

    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Generate multi-res images
    resolutions = [16, 24, 32, 48, 64, 128, 256]
    images = {res: render_icon_image(res) for res in resolutions}

    # Save 256x256 PNG
    png_path = assets_dir / "icon.png"
    images[256].save(str(png_path), "PNG")
    print(f"Generated PNG icon: {png_path}")

    # Save 512x512 high-res PNG for marketing / installer banner
    hires_image = render_icon_image(512)
    hires_path = assets_dir / "icon_512.png"
    hires_image.save(str(hires_path), "PNG")
    print(f"Generated High-Res PNG: {hires_path}")

    # Save Windows ICO
    ico_path = assets_dir / "icon.ico"
    # Using QIcon to bundle multi-resolution representations
    qicon = QIcon()
    for res, img in images.items():
        from PySide6.QtGui import QPixmap
        qicon.addPixmap(QPixmap.fromImage(img))

    # In Qt/PySide6, save icon directly or save via image
    images[256].save(str(ico_path), "ICO")
    print(f"Generated ICO icon: {ico_path}")


if __name__ == "__main__":
    main()
