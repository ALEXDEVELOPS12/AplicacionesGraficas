import flet as ft
import urllib.parse
import webbrowser
import os


def vista_detalle(page: ft.Page, pelicula: dict):

    # ── Breakpoints ────────────────────────────────────────────────────────────

    def layout():
        w = page.width or 900
        if w < 600:
            return "mobile"
        elif w < 1024:
            return "tablet"
        else:
            return "desktop"

    # ── Datos de la película ───────────────────────────────────────────────────

    titulo    = pelicula.get("Title", "Sin título")
    año       = pelicula.get("Year", "")
    rated     = pelicula.get("Rated", "")
    runtime   = pelicula.get("Runtime", "")
    genero    = pelicula.get("Genre", "")
    director  = pelicula.get("Director", "")
    actores   = pelicula.get("Actors", "")
    sinopsis  = pelicula.get("Plot", "Sin descripción disponible.")
    rating    = pelicula.get("imdbRating", "N/A")
    poster    = pelicula.get("Poster", "")
    awards    = pelicula.get("Awards", "")

    # ── Navegación ─────────────────────────────────────────────────────────────

    def ir_a_inicio(e):
        from PaginaInicio import vista_inicio
        page.on_resize = None
        page.clean()
        vista_inicio(page)

    def abrir_trailer(e):
        query = urllib.parse.quote(f"{titulo} {año} official trailer")
        url = f"https://www.youtube.com/results?search_query={query}"
        try:
            page.launch_url(url)
        except Exception:
            webbrowser.open(url)

    # ── Build ──────────────────────────────────────────────────────────────────

    def build():
        page.clean()
        mode = layout()
        w = page.width or 900

        if mode == "mobile":
            poster_w      = w * 0.45
            poster_h      = poster_w * 1.5
            font_titulo   = 20
            font_meta     = 12
            font_seccion  = 13
            font_texto    = 13
            padding_h     = 16
            horizontal    = False   # póster arriba, info abajo
        elif mode == "tablet":
            poster_w      = 200
            poster_h      = 300
            font_titulo   = 26
            font_meta     = 13
            font_seccion  = 14
            font_texto    = 14
            padding_h     = 28
            horizontal    = True
        else:  # desktop
            poster_w      = 260
            poster_h      = 390
            font_titulo   = 32
            font_meta     = 14
            font_seccion  = 15
            font_texto    = 15
            padding_h     = 60
            horizontal    = True

        # ── Navbar ─────────────────────────────────────────────────────────────
        navbar = ft.Container(
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.BLACK),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            content=ft.Row(
                [
                    ft.Container(
                        ink=True,
                        border_radius=8,
                        on_click=ir_a_inicio,
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW, color=ft.Colors.WHITE70, size=16),
                                ft.Text("Inicio", color=ft.Colors.WHITE70, size=14),
                            ],
                            spacing=4,
                            tight=True,
                        ),
                    ),
                    ft.Text(
                        "NicaPlex",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.RED_500,
                    ),
                    ft.Container(width=60),  # espaciador para centrar logo
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # ── Póster ─────────────────────────────────────────────────────────────
        if poster and poster != "N/A":
            img_poster = ft.Image(
                src=poster,
                width=poster_w,
                height=poster_h,
                fit=ft.BoxFit.COVER,
                border_radius=12,
            )
        else:
            img_poster = ft.Container(
                width=poster_w,
                height=poster_h,
                bgcolor=ft.Colors.GREY_900,
                border_radius=12,
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(ft.Icons.MOVIE, color=ft.Colors.GREY_600, size=60),
            )

        # ── Badges de metadata ─────────────────────────────────────────────────
        def badge(texto, color=ft.Colors.GREY_800):
            return ft.Container(
                bgcolor=color,
                border_radius=6,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                content=ft.Text(texto, size=font_meta, color=ft.Colors.WHITE),
            )

        badges = ft.Row(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=16),
                        ft.Text(f"{rating}", size=font_meta + 1,
                                color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=4,
                    tight=True,
                ),
                badge(año),
                badge(rated) if rated and rated != "N/A" else ft.Container(),
                badge(runtime) if runtime and runtime != "N/A" else ft.Container(),
            ],
            spacing=8,
            wrap=True,
        )

        # ── Géneros ────────────────────────────────────────────────────────────
        generos_row = ft.Row(
            [
                ft.Container(
                    bgcolor=ft.Colors.RED_900,
                    border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                    content=ft.Text(g.strip(), size=font_meta, color=ft.Colors.WHITE),
                )
                for g in genero.split(",") if g.strip()
            ],
            spacing=6,
            wrap=True,
        )

        # ── Botón trailer ──────────────────────────────────────────────────────
        btn_trailer = ft.Container(
            bgcolor=ft.Colors.RED_700,
            border_radius=10,
            ink=True,
            on_click=abrir_trailer,
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINE, color=ft.Colors.WHITE, size=20),
                    ft.Text("Ver Trailer", size=font_texto,
                            color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                ],
                spacing=8,
                tight=True,
            ),
        )

        # ── Sección de texto ───────────────────────────────────────────────────
        def seccion(label, valor):
            if not valor or valor == "N/A":
                return ft.Container()
            return ft.Column(
                [
                    ft.Text(label, size=font_seccion,
                            color=ft.Colors.WHITE54, weight=ft.FontWeight.BOLD),
                    ft.Text(valor, size=font_texto, color=ft.Colors.WHITE70),
                ],
                spacing=2,
            )

        # ── Info panel ─────────────────────────────────────────────────────────
        info = ft.Column(
            [
                ft.Text(titulo, size=font_titulo,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=8),
                badges,
                ft.Container(height=8),
                generos_row,
                ft.Container(height=16),
                btn_trailer,
                ft.Container(height=20),
                seccion("Sinopsis", sinopsis),
                ft.Container(height=12),
                seccion("Director", director),
                ft.Container(height=8),
                seccion("Reparto", actores),
                ft.Container(height=8),
                seccion("Premios", awards),
            ],
            spacing=0,
            expand=True,
        )

        # ── Layout horizontal (tablet/desktop) o vertical (mobile) ─────────────
        if horizontal:
            contenido = ft.Row(
                [
                    img_poster,
                    ft.Container(width=32),
                    ft.Container(content=info, expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            )
        else:
            contenido = ft.Column(
                [
                    ft.Row([img_poster], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=20),
                    info,
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            )

        cuerpo = ft.Container(
            expand=True,
            bgcolor=ft.Colors.BLACK,
            padding=ft.Padding.symmetric(horizontal=padding_h, vertical=24),
            content=contenido if not horizontal else ft.Column(
                [contenido],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        page.add(
            ft.Column(
                [navbar, cuerpo],
                spacing=0,
                expand=True,
            )
        )

    # ── Resize ─────────────────────────────────────────────────────────────────

    page.on_resize = lambda e: build()
    build()
