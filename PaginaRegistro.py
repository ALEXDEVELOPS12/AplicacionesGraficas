import flet as ft


def vista_registro(page: ft.Page):

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

    def ir_a_login(e):
        from PaginaLogin import vista_login
        page.on_resize = None
        page.clean()
        vista_login(page)

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
            "Crear cuenta",
            size=size_titulo,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.CENTER,
        )

        # ── Campo Usuario ──────────────────────────────────────────────────────
        campo_usuario = ft.TextField(
            hint_text="Nombre de usuario",
            keyboard_type=ft.KeyboardType.NAME,
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
            prefix_icon=ft.Icons.PERSON_OUTLINE,
        )

        # ── Campo Correo ───────────────────────────────────────────────────────
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

        # ── Botón Registrarse ──────────────────────────────────────────────────
        error_registro = ft.Text("", color=ft.Colors.RED_300, size=13, text_align=ft.TextAlign.CENTER)

        def handle_registro(e):
            from database import registrar_usuario, inicializar_bd
            inicializar_bd()
            resultado = registrar_usuario(
                campo_usuario.value or "",
                campo_email.value or "",
                campo_contrasena.value or ""
            )
            if resultado["ok"]:
                # Registro exitoso → ir al login con mensaje
                page.on_resize = None
                page.clean()
                from PaginaLogin import vista_login
                vista_login(page)
            else:
                error_registro.value = resultado["mensaje"]
                page.update()

        btn_registro = ft.Container(
            width=form_width,
            height=btn_height,
            bgcolor=ft.Colors.RED_700,
            border_radius=14,
            ink=True,
            alignment=ft.Alignment.CENTER,
            on_click=handle_registro,
            content=ft.Text(
                "Registrarse",
                size=font_btn,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
        )

        # ── Link Login ─────────────────────────────────────────────────────────
        texto_login = ft.Container(
            ink=True,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            alignment=ft.Alignment.CENTER,
            on_click=ir_a_login,
            content=ft.Text(
                "¿Ya tenés cuenta? Iniciar sesión",
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
                campo_usuario,
                ft.Container(height=16),
                campo_email,
                ft.Container(height=16),
                campo_contrasena,
                ft.Container(height=12),
                error_registro,
                ft.Container(height=16),
                btn_registro,
                ft.Container(height=12),
                texto_login,
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
