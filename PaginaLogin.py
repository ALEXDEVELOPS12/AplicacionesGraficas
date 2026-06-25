import flet as ft


def vista_login(page: ft.Page):

    # ── Breakpoints ────────────────────────────────────────────────────────────

    def layout():
        w = page.width or 800
        if w < 600:
            return "mobile"
        elif w < 1024:
            return "tablet"
        else:
            return "desktop"

    # ── Navegación ─────────────────────────────────────────────────────────────

    def ir_a_registro(e):
        from PaginaRegistro import vista_registro
        page.on_resize = None
        page.clean()
        vista_registro(page)

    def ir_a_inicio(e):
        from PaginaInicio import vista_inicio
        # Extrae el nombre de usuario del email (parte antes del @)
        email = campo_email.value or ""
        nombre = email.split("@")[0] if "@" in email else (email or "Usuario")
        page.on_resize = None
        page.clean()
        vista_inicio(page, nombre_usuario=nombre)

    # ── Build ──────────────────────────────────────────────────────────────────

    def build():
        page.clean()
        mode = layout()
        w = page.width or 800

        if mode == "mobile":
            size_titulo  = 32
            form_width   = w * 0.88
            btn_height   = 52
            font_btn     = 15
            font_campo   = 14
            font_sub     = 13
        elif mode == "tablet":
            size_titulo  = 42
            form_width   = 420
            btn_height   = 58
            font_btn     = 17
            font_campo   = 15
            font_sub     = 14
        else:  # desktop
            size_titulo  = 50
            form_width   = 480
            btn_height   = 64
            font_btn     = 18
            font_campo   = 16
            font_sub     = 15

        # ── Título ─────────────────────────────────────────────────────────────
        titulo = ft.Text(
            "Iniciar sesión",
            size=size_titulo,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        # ── Campo Email ────────────────────────────────────────────────────────
        campo_email = ft.TextField(
            hint_text="Correo electrónico",
            keyboard_type=ft.KeyboardType.EMAIL,
            width=form_width,
            text_size=font_campo,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            border_radius=12,
            border_color=ft.Colors.WHITE30,
            focused_border_color=ft.Colors.RED_400,
            focused_border_width=2,
            content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
        )

        # ── Campo Contraseña ───────────────────────────────────────────────────
        campo_contrasena = ft.TextField(
            hint_text="Contraseña",
            password=True,
            can_reveal_password=True,
            width=form_width,
            text_size=font_campo,
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            color=ft.Colors.WHITE,
            hint_style=ft.TextStyle(color=ft.Colors.WHITE54),
            border_radius=12,
            border_color=ft.Colors.WHITE30,
            focused_border_color=ft.Colors.RED_400,
            focused_border_width=2,
            content_padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )

        # ── Botón Iniciar sesión ───────────────────────────────────────────────
        error_login = ft.Text("", color=ft.Colors.RED_300, size=13, text_align=ft.TextAlign.CENTER)

        def handle_login(e):
            from database import login_usuario, inicializar_bd
            inicializar_bd()
            resultado = login_usuario(campo_email.value or "", campo_contrasena.value or "")
            print(f"Login resultado: {resultado}")  # debug
            if resultado["ok"]:
                page.on_resize = None
                page.clean()
                from PaginaInicio import vista_inicio
                vista_inicio(page, nombre_usuario=resultado["username"])
            else:
                error_login.value = resultado["mensaje"]
                page.update()

        btn_login = ft.Container(
            width=form_width,
            height=btn_height,
            bgcolor=ft.Colors.RED_700,
            border_radius=14,
            ink=True,
            alignment=ft.Alignment.CENTER,
            on_click=handle_login,
            content=ft.Text(
                "Iniciar sesión",
                size=font_btn,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
        )

        # ── Link Registrarse ───────────────────────────────────────────────────
        texto_registro = ft.Container(
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            alignment=ft.Alignment.CENTER,
            on_click=ir_a_registro,
            content=ft.Text(
                "¿No tenés cuenta? Registrarse",
                size=font_sub,
                color=ft.Colors.WHITE70,
                text_align=ft.TextAlign.CENTER,
            ),
        )

        # ── Botón volver ───────────────────────────────────────────────────────
        btn_volver = ft.Container(
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            # on_click=ir_a_bienvenida  ← descomentar cuando navegación esté lista
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW, color=ft.Colors.WHITE70, size=14),
                    ft.Text("Volver", size=font_sub, color=ft.Colors.WHITE70),
                ],
                spacing=4,
                tight=True,
            ),
        )

        # ── Formulario ─────────────────────────────────────────────────────────
        formulario = ft.Column(
            [
                titulo,
                ft.Container(height=32),
                campo_email,
                ft.Container(height=16),
                campo_contrasena,
                ft.Container(height=12),
                error_login,
                ft.Container(height=16),
                btn_login,
                ft.Container(height=12),
                texto_registro,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
        )

        # ── Overlay + fondo ────────────────────────────────────────────────────
        overlay = ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(0.55, ft.Colors.BLACK),
            content=ft.Column(
                [formulario],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
        )

        fondo = ft.Container(
            expand=True,
            image=ft.DecorationImage(
                src="fondo/fondobienvenida.jpg",
                fit=ft.BoxFit.COVER,
            ),
            content=overlay,
        )

        page.add(fondo)

    # ── Resize ─────────────────────────────────────────────────────────────────

    page.on_resize = lambda e: build()
    build()
