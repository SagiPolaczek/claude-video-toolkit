"""
Grid segment implementation for multi-source layouts.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

from .base import Segment

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig
    from video_toolkit.sources import ContentSource


@dataclass
class GridCell:
    """
    A single cell in a grid layout.

    Attributes:
        source: Content source for this cell
        position: (row, col) position, or None for auto-layout
        span: (row_span, col_span) for cells spanning multiple rows/cols
        label: Optional label text
        label_position: Where to show label ("top", "bottom", "none")
    """

    source: "ContentSource"
    position: Optional[Tuple[int, int]] = None
    span: Tuple[int, int] = (1, 1)
    label: Optional[str] = None
    label_position: str = "bottom"


@dataclass
class GridLayout:
    """
    Grid layout configuration.

    Defines the grid structure for auto-positioning cells.
    """

    rows: int
    cols: int
    cell_aspect_ratio: float = 16 / 9

    def auto_position(self, cells: List[GridCell]) -> List[GridCell]:
        """
        Assign positions to cells that don't have explicit positions.

        Args:
            cells: List of GridCells

        Returns:
            List of GridCells with positions assigned
        """
        result = []
        auto_index = 0

        for cell in cells:
            if cell.position is not None:
                result.append(cell)
            else:
                # Calculate auto position
                row = auto_index // self.cols
                col = auto_index % self.cols
                result.append(GridCell(
                    source=cell.source,
                    position=(row, col),
                    span=cell.span,
                    label=cell.label,
                    label_position=cell.label_position,
                ))
                auto_index += 1

        return result


@dataclass
class GridSegment(Segment):
    """
    Grid segment displaying multiple sources in a layout.

    Useful for:
    - Side-by-side comparisons
    - Result galleries
    - Multi-method comparisons
    """

    cells: List[GridCell] = field(default_factory=list)
    layout: Optional[GridLayout] = None
    gap: int = 5  # Pixels between cells
    background_color: Tuple[int, int, int] = (255, 255, 255)  # White by default
    label_color: Tuple[int, int, int] = (30, 30, 40)  # Dark text for white background
    label_font_size: int = 24

    def render(self, config: "ProjectConfig") -> Any:
        """
        Render this segment to a MoviePy clip.

        Args:
            config: Project configuration

        Returns:
            MoviePy VideoClip
        """
        from moviepy import ColorClip, CompositeVideoClip

        # Determine grid dimensions
        if self.layout is not None:
            rows, cols = self.layout.rows, self.layout.cols
            positioned_cells = self.layout.auto_position(self.cells)
        else:
            # Infer from cell positions
            positioned_cells = self.cells
            rows = max(c.position[0] + c.span[0] for c in positioned_cells if c.position)
            cols = max(c.position[1] + c.span[1] for c in positioned_cells if c.position)

        # Calculate cell dimensions
        total_gap_w = self.gap * (cols + 1)
        total_gap_h = self.gap * (rows + 1)
        cell_w = (config.width - total_gap_w) // cols
        cell_h = (config.height - total_gap_h) // rows

        # Determine duration
        if self.duration is not None:
            duration = self.duration
        else:
            # Use longest cell duration
            duration = self._get_max_cell_duration(positioned_cells, config)

        # Create background
        bg = ColorClip(
            size=config.dimensions,
            color=self.background_color,
            duration=duration,
        )

        clips = [bg]

        # Render each cell
        for cell in positioned_cells:
            if cell.position is None:
                continue

            row, col = cell.position
            row_span, col_span = cell.span

            # Calculate position
            x = self.gap + col * (cell_w + self.gap)
            y = self.gap + row * (cell_h + self.gap)

            # Calculate size (accounting for span)
            w = cell_w * col_span + self.gap * (col_span - 1)
            h = cell_h * row_span + self.gap * (row_span - 1)

            # Get and resize source clip
            cell_clip = cell.source.get_clip(config)

            # Resize to fit cell
            cell_clip = self._resize_to_fit(cell_clip, w, h)

            # Set duration
            cell_clip = cell_clip.with_duration(duration)

            # Position the clip
            cell_clip = cell_clip.with_position((x, y))

            clips.append(cell_clip)

            # Add label if present
            if cell.label and cell.label_position != "none":
                label_clip = self._create_label(
                    cell.label,
                    w,
                    x,
                    y,
                    h,
                    cell.label_position,
                    duration,
                    config,
                )
                if label_clip:
                    clips.append(label_clip)

        return CompositeVideoClip(clips, size=config.dimensions)

    def _resize_to_fit(self, clip: Any, target_w: int, target_h: int) -> Any:
        """Resize clip to fit within target dimensions."""
        clip_w, clip_h = clip.size

        scale_w = target_w / clip_w
        scale_h = target_h / clip_h
        scale = min(scale_w, scale_h)

        if scale != 1.0:
            clip = clip.resized(scale)

        return clip

    def _create_label(
        self,
        text: str,
        width: int,
        x: int,
        y: int,
        cell_height: int,
        position: str,
        duration: float,
        config: "ProjectConfig",
    ) -> Any:
        """Create a label clip."""
        try:
            from moviepy import TextClip

            font_size = int(self.label_font_size * config.scale_factor)
            label = TextClip(
                text=text,
                font_size=font_size,
                color=f"rgb{self.label_color}",
                font="Arial",
            )

            # Position label
            label_x = x + (width - label.w) // 2
            if position == "top":
                label_y = y - font_size - 5
            else:  # bottom
                label_y = y + cell_height + 5

            return label.with_position((label_x, label_y)).with_duration(duration)
        except Exception:
            return None

    def _get_max_cell_duration(
        self,
        cells: List[GridCell],
        config: "ProjectConfig",
    ) -> float:
        """Get the maximum duration from all cells."""
        max_duration = 0.0
        for cell in cells:
            try:
                clip = cell.source.get_clip(config)
                if hasattr(clip, "duration") and clip.duration:
                    max_duration = max(max_duration, clip.duration)
            except Exception:
                pass
        return max_duration if max_duration > 0 else 5.0

    def get_duration(self, config: "ProjectConfig") -> float:
        """Get duration from cells or explicit setting."""
        if self.duration is not None:
            return self.duration

        if self.layout is not None:
            positioned_cells = self.layout.auto_position(self.cells)
        else:
            positioned_cells = self.cells

        return self._get_max_cell_duration(positioned_cells, config)
