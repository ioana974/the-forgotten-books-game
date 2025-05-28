import pygame
from lib.config import *
from lib.assets import *

def draw_button(
    text,
    x, y,
    height,
    font_size=100,
    icon=None,
    text_color=(40, 40, 40),
    animated_paper=None,
    button_state=None,
    surface = screen,
):
    font = pygame.font.Font(FONT_PATH, font_size)

    offset_y = animated_paper.get_current_offset() if animated_paper else 0
    scroll_progress = animated_paper.scroll_progress if animated_paper else 1.0
    real_height = (
        animated_paper.base_image.get_height()
        if animated_paper and animated_paper.base_image
        else height
    )

    # Base scroll width (closed state)
    base_width = animated_paper.base_image.get_width() if animated_paper and animated_paper.base_image else height

    # Text + icon width for full extension
    text_surface = font.render(text, True, text_color)
    spacing = 30 if icon else 0
    text_width = text_surface.get_width()
    animated_width = text_width + 20 


    # Set animation length once

    if animated_paper and animated_paper.length != animated_width:
        animated_paper.set_length(animated_width)

    # Hitbox = base_width + animated scroll
    visible_width = base_width + int(scroll_progress * animated_width)

    # Check mouse inside dynamic hitbox
    mouse_x, mouse_y = pygame.mouse.get_pos()
    HOVER_MARGIN = 23
    inside_strict = (
        x <= mouse_x <= x + visible_width and
        y + offset_y <= mouse_y <= y + offset_y + real_height
    )

    inside_relaxed = (
        x - HOVER_MARGIN <= mouse_x <= x + visible_width + HOVER_MARGIN and
        y + offset_y - HOVER_MARGIN <= mouse_y <= y + offset_y + real_height + HOVER_MARGIN
    )

    if button_state is not None:
        if button_state.get("hovered", False):
            # Only stop hovering if completely outside relaxed margin
            if not inside_relaxed:
                button_state["hovered"] = False
        else:
            if inside_strict:
                button_state["hovered"] = True

        is_hovered = button_state["hovered"]
    else:
        is_hovered = inside_strict  # fallback


    if animated_paper:
        if is_hovered:
            animated_paper.start_roll()
        else:
            animated_paper.reverse_roll()
        animated_paper.update()
        animated_paper.draw(surface, x, y)
    else:
        pygame.draw.rect(surface, BUTTON_COLOR, (x, y, visible_width, height))
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, (x, y, visible_width, height), 3)

    # ICON (only left of paper when closed/unrolling)
    text_x_offset = 0
    if icon:
        icon_height = int(real_height * 0.65)
        icon_scaled = pygame.transform.smoothscale(icon, (icon_height, icon_height))
        icon_y = y + offset_y + (real_height - icon_height) // 2
        surface.blit(icon_scaled, (x + 10, icon_y))
        text_x_offset = icon_height + spacing


    # TEXT (letter-by-letter reveal based on scroll_progress)
    if scroll_progress > 0.1:
        reveal_ratio = scroll_progress
        max_chars = max(1, int(len(text) * reveal_ratio))
        partial_text = text[:max_chars]

        text_surface = font.render(partial_text, True, text_color)
        text_surface.set_alpha(int(255 * scroll_progress))

        text_x = x + text_x_offset
        text_y = y + offset_y + (real_height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))

        # DEBUG: show the text hitbox
        TEXT_HITBOX_DEBUG = False
        if TEXT_HITBOX_DEBUG:
            pygame.draw.rect(
                surface,
                (0, 255, 0),
                (text_x, text_y, text_surface.get_width(), text_surface.get_height()),
                2
            )


    # DEBUG: draw the hitbox outline
    HITBOX_DEBUG = False
    if HITBOX_DEBUG:
        pygame.draw.rect(surface, (255, 0, 0), (x, y + offset_y, visible_width, real_height), 2)

    return is_hovered
