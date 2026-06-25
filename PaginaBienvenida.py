import flet as ft


def vista_bienvenida(page: ft.Page):
    page.title = "NicaPlex"
    page.padding = 0
    page.bgcolor = ft.Colors.TRANSPARENT

    page.fonts = {
        "GreatVibes": "https://raw.githubusercontent.com/google/fonts/main/ofl/greatvibes/GreatVibes-Regular.ttf"
    }

    # Tamaños en los diferentes dispositivos

    def layout():
        w = page.width or 800
        if w < 600:
            return "mobile"
        elif w < 1024:
            return "tablet"
        else:
            return "desktop"
            

    # Navegación

    def ir_a_login(e):
        from PaginaLogin import vista_login
        page.on_resize = None
        page.clean()
        vista_login(page)

    def ir_a_registro(e):
        from PaginaRegistro import vista_registro
        page.on_resize = None
        page.clean()
        vista_registro(page)

    # construccion de la vista

    def build():
        page.clean()
        mode = layout()
        w = page.width or 800

        if mode == "mobile":
            size_bienvenido = 36
            size_nicaplex   = 62
            btn_width       = w * 0.78
            btn_height      = 52
            font_btn        = 15
            font_reg        = 14
        elif mode == "tablet":
            size_bienvenido = 46
            size_nicaplex   = 80
            btn_width       = 360
            btn_height      = 58
            font_btn        = 17
            font_reg        = 15
        else:  # desktop
            size_bienvenido = 56
            size_nicaplex   = 100
            btn_width       = 420
            btn_height      = 64
            font_btn        = 19
            font_reg        = 16

        # ── Texto de Bienvenido a NicaPlex
        texto_bienvenida = ft.Column(
            [
                ft.Text(
                    "Bienvenido a",
                    font_family="GreatVibes",
                    size=size_bienvenido,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "NicaPlex",
                    font_family="GreatVibes",
                    size=size_nicaplex,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

        # Botón Iniciar sesión
        btn_login = ft.Container(
            width=btn_width,
            height=btn_height,
            bgcolor=ft.Colors.RED_700,
            border_radius=14,
            ink=True,
            alignment=ft.Alignment.CENTER,
            on_click=ir_a_login,
            content=ft.Text(
                "Iniciar sesión",
                size=font_btn,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
        )

        # Link Registrarse
        texto_registro = ft.Container(
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            alignment=ft.Alignment.CENTER,
            on_click=ir_a_registro,
            content=ft.Text(
                "¿No tenés cuenta? Registrarse",
                size=font_reg,
                color=ft.Colors.WHITE70,
                text_align=ft.TextAlign.CENTER,
            ),
        )

        # Bloque central
        bloque = ft.Column(
            [
                texto_bienvenida,
                ft.Container(height=48),
                btn_login,
                ft.Container(height=12),
                texto_registro,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        )

        # ── Overlay oscuro
        overlay = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.50, ft.Colors.BLACK),
            content=ft.Column(
                [bloque],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
        )

        # Imagen de Fondo
        fondo = ft.Container(
            expand=True,
            image=ft.DecorationImage(
                src="fondo/fondobienvenida.jpg",
                fit=ft.BoxFit.COVER,
            ),
            content=overlay,
        )

        page.add(fondo)

    # Resize
    page.on_resize = lambda e: build()
    build()


def main(page: ft.Page):
    vista_bienvenida(page)


if __name__ == "__main__":
    import os
    # En producción web (Railway/servidor) usar WEB_BROWSER
    # En local usar la vista por defecto (desktop nativo)
    port = int(os.environ.get("PORT", 8080))
    ft.app(
        main,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER if os.environ.get("PORT") else ft.AppView.FLET_APP,
        port=port,
    )
