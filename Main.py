from ttkbootstrap import Window
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk
import sys
import os

# importaciones Comunes 
from Core.Common.logger import setup_logger
from Core.Common.config import load_config, save_config
from Core.Styles.modern_styles import ModernStyleManager
from Core.Styles.base_components import MenuFrame, StyledLabel, InfoFrame, SeparatorFrame, BaseFrame
from Core.Styles.bootstrap_theme_editor import CustomThemeManager

# Paginas 
from Core.Pages.Resumenes.resumen import ResumenesFrame
from Core.Pages.Compras.Compras import ComprasFrame
from Core.Pages.Produccion.produccion import ProduccionFrame
from Core.Pages.Ventas.ventas import VentasFrame
from Core.Pages.Productos.Productos import ProductosFrame
from Core.Pages.Gastos.gastos import GastosFrame
from Core.Common.settings import SettingsFrame


class MainApplication:
    """Aplicación principal con Dashboard y Sistema de Temas Moderno"""
    
    MENU_ITEMS = [
        ("🛒 Compras", "compras"),
        ("📈 Resúmenes", "resumenes"),
        ("🏭 Producción", "produccion"),
        ("📦 Productos", "productos"),
        ("💰 Ventas", "ventas"),
        ("💸 Gastos", "gastos"),
        ("⚙️ Ajustes", "settings"),
    ]
    
    PAGES = {
        "compras": ComprasFrame,
        "settings": SettingsFrame,
        "resumenes": ResumenesFrame,
        "produccion": ProduccionFrame,
        "ventas": VentasFrame,
        "gastos": GastosFrame,
        "productos": ProductosFrame,
    }

    def __init__(self, root):
        self.root = root
        self.root.title("📱 Sistema de Economía v3.2 - Moderno")
        self.root.geometry("1500x900")
        
        self.logger = setup_logger()
        self.config = load_config()
        self.current_page = None
        self.current_page_name = None
        self.current_theme = self.config.get("theme", "solar")
        
        # Aplicar estilos modernos
        ModernStyleManager.configure_modern_styles(self.root.style, self.current_theme)
        
        # Colores según tema
        self.menu_bg = ModernStyleManager.get_bg_color(self.current_theme)
        self.menu_fg = ModernStyleManager.get_fg_color(self.current_theme)
        self.accent = ModernStyleManager.get_accent_color(self.current_theme)
        
        self.logger.info("="*60)
        self.logger.info("✅ APLICACIÓN INICIADA - VERSIÓN 3.2 MODERNA")
        self.logger.info(f"📱 Tema actual: {self.current_theme}")
        self.logger.info("="*60)
        
        self.setup_ui()
        self.show_page("compras")
        
        self.root.bind("<Escape>", self.confirm_exit)
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
    
    def setup_ui(self):
        """Configura interfaz principal"""
        
        # MENÚ LATERAL - Con background consistente
        self.menu_frame = MenuFrame(self.root, theme_name=self.current_theme, width=280)
        self.menu_frame.pack(side=LEFT, fill=Y, padx=(10, 5), pady=10)
        
        # Logo
        self._create_logo()
        
        SeparatorFrame(self.menu_frame, height=10, theme_name=self.current_theme).pack()
        
        # Botones del menú
        for label, page_name in self.MENU_ITEMS:
            btn = tk.Button(
                self.menu_frame, text=label,
                command=lambda p=page_name: self.show_page(p),
                width=26, relief="flat", cursor="hand2",
                bg="#007bff", fg="white", font=("Segoe UI", 9, "bold"),
                activebackground="#0056b3", activeforeground="white",
                bd=0, highlightthickness=0
            )
            btn.pack(pady=5, padx=10, fill=X)
        
        SeparatorFrame(self.menu_frame, height=20, theme_name=self.current_theme).pack()
        
        # Info
        info_items = ["• Temas Modernos: ✓", "• Reportes: ✓", "• Base de Datos: ✓"]
        info = InfoFrame(
            self.menu_frame, 
            title="INFORMACIÓN",
            items=info_items,
            theme_name=self.current_theme
        )
        info.pack(fill=X, padx=10)
        
        # Espaciador
        SeparatorFrame(self.menu_frame, height=40, theme_name=self.current_theme).pack(expand=True)
        
        # === BOTONES INFERIORES ===
        reload_btn = tk.Button(
            self.menu_frame, text="🔄 Recargar",
            command=self.reload_app,
            width=26, relief="flat", cursor="hand2",
            bg="#17a2b8", fg="white", font=("Segoe UI", 9, "bold"),
            activebackground="#138496", activeforeground="white",
            bd=0, highlightthickness=0
        )
        reload_btn.pack(pady=5, padx=10, fill=X, side=BOTTOM)
        
        exit_btn = tk.Button(
            self.menu_frame, text="🚪 Salir",
            command=self.confirm_exit,
            width=26, relief="flat", cursor="hand2",
            bg="#dc3545", fg="white", font=("Segoe UI", 9, "bold"),
            activebackground="#c82333", activeforeground="white",
            bd=0, highlightthickness=0
        )
        exit_btn.pack(pady=5, padx=10, fill=X, side=BOTTOM)
        
        # CONTENIDO PRINCIPAL
        self.content_frame = BaseFrame(self.root, theme_name=self.current_theme)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)
    
    def _create_logo(self):
        """Crea la sección del logo"""
        logo_frame = MenuFrame(self.menu_frame, theme_name=self.current_theme)
        logo_frame.pack(fill=X, pady=(20, 10), padx=10)
        
        logo_emoji = StyledLabel(
            logo_frame, text="📱", label_type="title",
            theme_name=self.current_theme
        )
        logo_emoji.set_accent()
        logo_emoji.pack()
        
        logo_title = StyledLabel(
            logo_frame, text="ECONOMÍA", label_type="heading",
            theme_name=self.current_theme
        )
        logo_title.set_accent()
        logo_title.pack()
        
        logo_version = StyledLabel(
            logo_frame, text="v3.2 Moderno", label_type="small",
            theme_name=self.current_theme
        )
        logo_version.pack()
    
    def show_page(self, page_name):
        """Muestra página solicitada"""
        if self.current_page:
            self.current_page.destroy()
        
        if page_name not in self.PAGES:
            self.logger.warning(f"Página desconocida: {page_name}")
            return
        
        try:
            PageClass = self.PAGES[page_name]
            self.current_page = PageClass(self.content_frame)
            self.current_page.pack(fill=BOTH, expand=True)
            self.current_page_name = page_name
            self.logger.info(f"✅ Página cargada: {page_name}")
        
        except Exception as e:
            self.logger.error(f"Error cargando {page_name}: {e}")
            messagebox.showerror("Error", f"Error cargando página:\n{e}")
    
    def reload_app(self):
        """Recarga la aplicación"""
        self.logger.info("🌀 Recargando la aplicación...")
        messagebox.showinfo("🔄 Recargando", "La aplicación se reiniciará...")
        
        self.root.after(300, self._do_reload)
    
    def _do_reload(self):
        """Ejecuta la recarga"""
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def confirm_exit(self, event=None):
        """Confirma salida"""
        if messagebox.askyesno("Confirmar", "¿Salir de la aplicación?"):
            self.logger.info("🚪 Aplicación cerrada correctamente")
            self.root.quit()


def main():
    """Punto de entrada con soporte para temas modernos"""
    config = load_config()
    theme = config.get("theme", "solar")
    
    # Validar tema
    if not CustomThemeManager.is_valid_bootstrap_theme(theme):
        theme = "solar"
        config["theme"] = theme
        save_config(config)
    
    root = Window(themename=theme)
    
    # Aplicar tema personalizado si existe
    custom_themes = CustomThemeManager.load_custom_themes()
    if theme in custom_themes:
        CustomThemeManager.apply_custom_theme(root.style, custom_themes[theme])
    
    app = MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()