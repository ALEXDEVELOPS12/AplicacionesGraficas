import os
import json
import time
import flet as ft
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OMDB_KEY   = os.environ.get("OMDB_KEY", "d00b9e68")
OMDB_URL   = "https://www.omdbapi.com/"
CACHE_FILE = Path(__file__).parent / ".omdb_cache.json"
CACHE_TTL  = 60 * 60 * 24

# ── Catálogo ───────────────────────────────────────────────────────────────────
CATEGORIAS = {
    "Acción": [
        "The Dark Knight", "Mad Max: Fury Road", "John Wick",
        "Mission: Impossible - Ghost Protocol", "Die Hard", "Gladiator",
        "Top Gun: Maverick", "The Raid", "Heat", "Speed"
    ],
    "Ciencia Ficción": [
        "Inception", "Interstellar", "The Matrix",
        "Avatar", "Blade Runner 2049", "Arrival",
        "Dune", "Gravity", "Ex Machina", "The Martian"
    ],
    "Comedia": [
        "The Grand Budapest Hotel", "Superbad", "Home Alone",
        "Bridesmaids", "The Hangover", "Knives Out",
        "Game Night", "21 Jump Street", "Crazy Rich Asians", "About Time"
    ],
    "Drama": [
        "The Shawshank Redemption", "Forrest Gump", "The Godfather",
        "Schindler's List", "Fight Club", "Parasite",
        "Whiplash", "The Pursuit of Happyness", "A Beautiful Mind", "Good Will Hunting"
    ],
}

# ── Caché en disco ─────────────────────────────────────────────────────────────

def _leer_cache() -> dict:
    try:
        if CACHE_FILE.exists():
            data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if time.time() - data.get("_ts", 0) < CACHE_TTL:
                return data
    except Exception:
        pass
    return {}

def _guardar_cache(data: dict):
    try:
        data["_ts"] = time.time()
        CACHE_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

_cache_disco = _leer_cache()

# ── OMDB ───────────────────────────────────────────────────────────────────────

def buscar_pelicula_titulo(titulo: str) -> dict:
    if titulo in _cache_disco:
        return _cache_disco[titulo]
    try:
        r = requests.get(OMDB_URL, params={"t": titulo, "apikey": OMDB_KEY}, timeout=6)
        data = r.json()
        if data.get("Response") == "True":
            if not data.get("Poster") or data["Poster"] == "N/A":
                data["Poster"] = "fondo/fondo_peliculas.png"
            _cache_disco[titulo] = data
            _guardar_cache(_cache_disco)
            return data
    except Exception as e:
        print(f"OMDB error '{titulo}': {e}")
    return {"Title": titulo, "Year": "", "Poster": "fondo/fondo_peliculas.png", "imdbRating": "N/A"}

def buscar_peliculas_query(query: str) -> list:
    try:
        r = requests.get(OMDB_URL, params={"s": query, "apikey": OMDB_KEY, "type": "movie"}, timeout=6)
        data = r.json()
        if data.get("Response") == "True":
            return data.get("Search", [])
    except Exception:
        pass
    return []

def cargar_categoria_paralelo(titulos: list) -> list:
    resultados = [None] * len(titulos)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futuros = {executor.submit(buscar_pelicula_titulo, t): i for i, t in enumerate(titulos)}
        for futuro in as_completed(futuros):
            idx = futuros[futuro]
            try:
                resultados[idx] = futuro.result()
            except Exception:
                resultados[idx] = {"Title": titulos[idx], "Year": "",
                                   "Poster": "fondo/fondo_peliculas.png", "imdbRating": "N/A"}
    return resultados

# ── Vista ──────────────────────────────────────────────────────────────────────

def vista_inicio(page: ft.Page, nombre_usuario: str = "Usuario"):

    busqueda_activa     = {"valor": False}
    menu_activo         = {"valor": False}
    datos_cache         = {}

    # ── Breakpoints ────────────────────────────────────────────────────────────

    def layout():
        w = page.width or 900
        if w < 600:  return "mobile"
        if w < 1024: return "tablet"
        return "desktop"

    # ── Widgets reutilizables ──────────────────────────────────────────────────

    def make_spinner(msg="Cargando películas..."):
        return ft.Container(
            expand=True,
            bgcolor=ft.Colors.BLACK,
            content=ft.Column([
                ft.ProgressRing(color=ft.Colors.RED_500),
                ft.Text(msg, color=ft.Colors.WHITE60, size=14),
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               spacing=16, expand=True),
        )

    # ── Contenedor raíz (nunca se remueve, solo se actualiza) ──────────────────
    raiz = ft.Column(expand=True, spacing=0)
    raiz.controls.append(make_spinner())
    page.add(raiz)
    page.update()

    def set_contenido(controles: list):
        """Reemplaza el contenido del contenedor raíz y fuerza repintado."""
        raiz.controls.clear()
        raiz.controls.extend(controles)
        raiz.update()

    def tarjeta_pelicula(pelicula):
        mode = layout()
        card_w, card_h = (110,165) if mode=="mobile" else (130,195) if mode=="tablet" else (150,225)
        font_t, font_s = (10,9)    if mode=="mobile" else (11,10)   if mode=="tablet" else (12,11)

        poster_url = pelicula.get("Poster","")
        titulo     = pelicula.get("Title","Sin título")
        año        = pelicula.get("Year","")
        rating     = pelicula.get("imdbRating","N/A")

        imagen = (
            ft.Image(src=poster_url, width=card_w, height=card_h,
                     fit=ft.BoxFit.COVER, border_radius=ft.BorderRadius(8,8,0,0))
            if poster_url and poster_url != "N/A"
            else ft.Container(width=card_w, height=card_h, bgcolor=ft.Colors.GREY_900,
                              border_radius=ft.BorderRadius(8,8,0,0),
                              alignment=ft.Alignment.CENTER,
                              content=ft.Icon(ft.Icons.MOVIE, color=ft.Colors.GREY_600, size=40))
        )

        def abrir_detalle(e, p=pelicula):
            from PaginaDetalle import vista_detalle
            page.on_resize = None
            page.clean()
            vista_detalle(page, p)

        return ft.Container(
            width=card_w, border_radius=8, bgcolor=ft.Colors.GREY_900,
            ink=True, clip_behavior=ft.ClipBehavior.HARD_EDGE, on_click=abrir_detalle,
            content=ft.Column([
                imagen,
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                    content=ft.Column([
                        ft.Text(titulo, size=font_t, color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD, max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=10),
                            ft.Text(f"{rating}  {año}", size=font_s, color=ft.Colors.WHITE60),
                        ], spacing=2),
                    ], spacing=2),
                ),
            ], spacing=0),
        )

    def fila_categoria(nombre, peliculas_data):
        mode     = layout()
        font_cat = 18 if mode=="desktop" else 15 if mode=="tablet" else 13
        return ft.Column([
            ft.Text(nombre, size=font_cat, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Row([tarjeta_pelicula(p) for p in peliculas_data if p],
                   scroll=ft.ScrollMode.AUTO, spacing=12),
        ], spacing=8)

    # ── Navbar ─────────────────────────────────────────────────────────────────

    campo_busqueda_ref = ft.Ref[ft.TextField]()

    def toggle_busqueda(e):
        busqueda_activa["valor"] = not busqueda_activa["valor"]
        menu_activo["valor"] = False
        mostrar_catalogo()

    def toggle_menu(e):
        menu_activo["valor"] = not menu_activo["valor"]
        busqueda_activa["valor"] = False
        mostrar_catalogo()

    def cerrar_sesion(e):
        from PaginaBienvenida import vista_bienvenida
        page.on_resize = None
        page.clean()
        vista_bienvenida(page)

    def ejecutar_busqueda(e):
        query = (campo_busqueda_ref.current.value or "").strip()
        if query:
            busqueda_activa["valor"] = False
            iniciar_busqueda(query)

    def build_navbar(mostrar_volver=False, volver_fn=None):
        mode      = layout()
        font_logo = 22 if mode=="desktop" else 18

        # En móvil agregar padding top para respetar la status bar
        pad_top = 44 if mode == "mobile" else 12

        if busqueda_activa["valor"]:
            return ft.Container(
                bgcolor=ft.Colors.with_opacity(0.97, ft.Colors.BLACK),
                padding=ft.Padding(left=20, right=20, top=pad_top, bottom=10),
                content=ft.Row([
                    ft.Text("NicaPlex", size=font_logo, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.RED_500),
                    ft.TextField(
                        ref=campo_busqueda_ref,
                        hint_text="Buscar película...",
                        hint_style=ft.TextStyle(color=ft.Colors.WHITE38),
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
                        border_radius=10, border_color=ft.Colors.WHITE24,
                        focused_border_color=ft.Colors.RED_400,
                        content_padding=ft.Padding.symmetric(horizontal=14, vertical=8),
                        text_size=14, expand=True, autofocus=True,
                        on_submit=ejecutar_busqueda, suffix_icon=ft.Icons.SEARCH,
                    ),
                    ft.Container(ink=True, border_radius=8, padding=ft.Padding.all(6),
                                 on_click=toggle_busqueda,
                                 content=ft.Icon(ft.Icons.CLOSE, color=ft.Colors.WHITE70, size=22)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=12),
            )

        izquierda = (
            ft.Container(ink=True, border_radius=8, padding=ft.Padding.all(6),
                         on_click=volver_fn,
                         content=ft.Row([
                             ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW, color=ft.Colors.WHITE70, size=16),
                             ft.Text("Inicio", color=ft.Colors.WHITE70, size=14),
                         ], spacing=4, tight=True))
            if mostrar_volver
            else ft.Text("NicaPlex", size=font_logo, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_500)
        )

        derecha = ft.Row([
            ft.Container(ink=True, border_radius=8, padding=ft.Padding.all(6),
                         on_click=toggle_busqueda,
                         content=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE70, size=22)),
            ft.Container(ink=True, border_radius=8, padding=ft.Padding.all(6),
                         on_click=toggle_menu,
                         content=ft.Icon(ft.Icons.PERSON_OUTLINE, color=ft.Colors.WHITE70, size=22)),
        ], spacing=8) if not mostrar_volver else ft.Container(
            ink=True, border_radius=8, padding=ft.Padding.all(6),
            on_click=toggle_busqueda,
            content=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.WHITE70, size=22),
        )

        centro = ft.Text("NicaPlex", size=font_logo, weight=ft.FontWeight.BOLD,
                         color=ft.Colors.RED_500) if mostrar_volver else ft.Container()

        return ft.Container(
            bgcolor=ft.Colors.with_opacity(0.97, ft.Colors.BLACK),
            padding=ft.Padding(left=20, right=20, top=pad_top, bottom=12),
            content=ft.Row([izquierda, centro, derecha],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        )

    def build_menu():
        if not menu_activo["valor"]:
            return ft.Container(height=0)
        return ft.Container(
            bgcolor=ft.Colors.GREY_900,
            border_radius=ft.BorderRadius(0,0,12,12),
            padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            content=ft.Column([
                ft.Row([
                    ft.Container(width=40, height=40, bgcolor=ft.Colors.RED_700,
                                 border_radius=20, alignment=ft.Alignment.CENTER,
                                 content=ft.Text(nombre_usuario[0].upper(), size=18,
                                                 weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
                    ft.Column([
                        ft.Text(nombre_usuario, size=15, color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("Mi cuenta", size=12, color=ft.Colors.WHITE54),
                    ], spacing=2),
                ], spacing=12),
                ft.Divider(color=ft.Colors.WHITE12, height=20),
                ft.Container(ink=True, border_radius=8,
                             padding=ft.Padding.symmetric(horizontal=8, vertical=8),
                             on_click=cerrar_sesion,
                             content=ft.Row([
                                 ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED_400, size=18),
                                 ft.Text("Cerrar sesión", size=14, color=ft.Colors.RED_400),
                             ], spacing=10)),
            ], spacing=0),
        )

    # ── Mostrar catálogo ───────────────────────────────────────────────────────

    def mostrar_catalogo():
        mode      = layout()
        padding_h = 16 if mode=="mobile" else 24 if mode=="tablet" else 40
        filas = ft.Column(
            [fila_categoria(cat, pelis) for cat, pelis in datos_cache.items()],
            spacing=28, scroll=ft.ScrollMode.AUTO, expand=True,
        )
        cuerpo = ft.Container(
            expand=True, bgcolor=ft.Colors.BLACK,
            padding=ft.Padding.symmetric(horizontal=padding_h, vertical=20),
            content=filas,
        )
        set_contenido([build_navbar(), build_menu(), cuerpo])

    # ── Búsqueda ───────────────────────────────────────────────────────────────

    def iniciar_busqueda(query):
        set_contenido([make_spinner(f'Buscando "{query}"...')])

        def buscar():
            resultados_basicos = buscar_peliculas_query(query)[:10]
            detallados = []
            if resultados_basicos:
                with ThreadPoolExecutor(max_workers=10) as ex:
                    futuros = {ex.submit(buscar_pelicula_titulo, r.get("Title","")): r
                               for r in resultados_basicos}
                    for f in as_completed(futuros):
                        try:
                            d = f.result()
                            if d: detallados.append(d)
                        except Exception:
                            pass

            mode      = layout()
            padding_h = 16 if mode=="mobile" else 24 if mode=="tablet" else 40
            font_cat  = 18 if mode=="desktop" else 15

            contenido_res = (
                ft.Column([
                    ft.Text(f'Resultados para "{query}"', size=font_cat,
                            weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row([tarjeta_pelicula(p) for p in detallados],
                           scroll=ft.ScrollMode.AUTO, spacing=12),
                ], spacing=8)
                if detallados else
                ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, color=ft.Colors.WHITE38, size=48),
                    ft.Text(f'No se encontraron resultados para "{query}"',
                            size=14, color=ft.Colors.WHITE54, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            )

            cuerpo = ft.Container(
                expand=True, bgcolor=ft.Colors.BLACK,
                padding=ft.Padding.symmetric(horizontal=padding_h, vertical=20),
                content=ft.Column([contenido_res], spacing=28,
                                  scroll=ft.ScrollMode.AUTO, expand=True),
            )

            def mostrar():
                set_contenido([
                    build_navbar(mostrar_volver=True, volver_fn=lambda e: mostrar_catalogo()),
                    cuerpo
                ])

            page.run_thread(mostrar)

        threading.Thread(target=buscar, daemon=True).start()

    # ── Carga inicial ──────────────────────────────────────────────────────────
    # La estructura de UI se construye aquí en el hilo principal.
    # Solo las peticiones HTTP van a hilos secundarios.

    mode      = layout()
    padding_h = 16 if mode=="mobile" else 24 if mode=="tablet" else 40
    font_cat  = 18 if mode=="desktop" else 15 if mode=="tablet" else 13

    filas_col = ft.Column(spacing=28, scroll=ft.ScrollMode.AUTO, expand=True)
    cuerpo_principal = ft.Container(
        expand=True, bgcolor=ft.Colors.BLACK,
        padding=ft.Padding.symmetric(horizontal=padding_h, vertical=20),
        content=filas_col,
    )

    # Reemplazar el spinner inicial con la estructura real
    raiz.controls.clear()
    raiz.controls.extend([build_navbar(), build_menu(), cuerpo_principal])
    raiz.update()

    lock = threading.Lock()

    def cargar_cat(nombre, titulos):
        peliculas = cargar_categoria_paralelo(titulos)
        datos_cache[nombre] = peliculas
        fila = ft.Column([
            ft.Text(nombre, size=font_cat, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Row([tarjeta_pelicula(p) for p in peliculas if p],
                   scroll=ft.ScrollMode.AUTO, spacing=12),
        ], spacing=8)

        # Ejecutar el update en el hilo del event loop de Flet (fix para desktop)
        def agregar_fila():
            with lock:
                filas_col.controls.append(fila)
                page.update()

        page.run_thread(agregar_fila)

    hilos = [threading.Thread(target=cargar_cat, args=(n, t), daemon=True)
             for n, t in CATEGORIAS.items()]
    for h in hilos: h.start()

    # ── Resize ─────────────────────────────────────────────────────────────────

    page.on_resize = lambda e: mostrar_catalogo() if datos_cache else None
