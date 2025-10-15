"""
Interface graphique de l'application Wigor Viewer.
Utilise Tkinter pour afficher l'emploi du temps d'un étudiant EPSI.
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

try:
    from ..auth.cookies_auth import build_session_from_cookie_header, is_authenticated
    from .timetable_parser import parse_wigor_html
    from .wigor_api import fetch_wigor_html
except ImportError:
    # Imports absolus pour exécution directe
    from auth.cookies_auth import build_session_from_cookie_header, is_authenticated
    from src.timetable_parser import parse_wigor_html
    from src.wigor_api import fetch_wigor_html

# Configuration du logger
logger = logging.getLogger(__name__)


class WigorViewerGUI:
    """Interface graphique principale de Wigor Viewer."""

    def __init__(self):
        """Initialise l'interface graphique."""
        self.root = tk.Tk()
        self.root.title("Wigor Viewer")
        self.root.geometry("1200x720")
        self.root.resizable(True, True)

        # Variables
        self.url_var = tk.StringVar(
            value="https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS"
        )
        self.cookie_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Prêt")
        self.connection_status_var = tk.StringVar(value="Non testé")
        self.login_status_var = tk.StringVar(value="Non connecté")

        # Données
        self.courses_data = []
        self.session = None  # Session authentifiée réutilisable

        self._create_widgets()
        self._setup_layout()

        logger.info("Interface graphique initialisée")

    def _create_widgets(self):
        """Crée tous les widgets de l'interface."""

        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configuration des colonnes/lignes
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(12, weight=1)

        # Titre
        title_label = ttk.Label(main_frame, text="Wigor Viewer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Champ URL
        ttk.Label(main_frame, text="URL Wigor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)

        # === SECTION AUTHENTIFICATION ===
        # Séparateur
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        # Titre section auth
        auth_label = ttk.Label(main_frame, text="Authentification", font=("Arial", 12, "bold"))
        auth_label.grid(row=3, column=0, columnspan=3, pady=(5, 10))

        # Champ Identifiant
        ttk.Label(main_frame, text="Identifiant:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=60)
        self.username_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)

        # Champ Mot de passe
        ttk.Label(main_frame, text="Mot de passe:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(
            main_frame, textvariable=self.password_var, width=60, show="*"
        )
        self.password_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)

        # Bouton Se connecter avec identifiants
        login_frame = ttk.Frame(main_frame)
        login_frame.grid(row=6, column=0, columnspan=3, pady=10)

        self.login_btn = ttk.Button(
            login_frame, text="Se connecter avec identifiants", command=self._login_with_credentials
        )
        self.login_btn.pack(side=tk.LEFT, padx=5)

        # Statut de connexion
        self.login_status_label = ttk.Label(
            login_frame, textvariable=self.login_status_var, foreground="gray"
        )
        self.login_status_label.pack(side=tk.LEFT, padx=10)

        # === SECTION COOKIE MANUEL ===
        # Séparateur
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        # Champ Cookie multi-ligne
        ttk.Label(main_frame, text="Cookie (copié depuis Chrome):").grid(
            row=8, column=0, sticky=(tk.W, tk.N), pady=5
        )

        # Frame pour le cookie avec scrollbar
        cookie_frame = ttk.Frame(main_frame)
        cookie_frame.grid(row=8, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        cookie_frame.columnconfigure(0, weight=1)

        # Text widget pour cookie multi-ligne
        self.cookie_text = tk.Text(cookie_frame, height=4, width=60, wrap=tk.WORD)
        cookie_scroll = ttk.Scrollbar(
            cookie_frame, orient=tk.VERTICAL, command=self.cookie_text.yview
        )
        self.cookie_text.configure(yscrollcommand=cookie_scroll.set)

        self.cookie_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        cookie_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Frame pour les boutons cookie
        cookie_btn_frame = ttk.Frame(main_frame)
        cookie_btn_frame.grid(row=8, column=2, padx=(5, 0), pady=5, sticky=tk.N)

        # Bouton Tester connexion
        self.test_btn = ttk.Button(
            cookie_btn_frame, text="Tester connexion", command=self._test_connection
        )
        self.test_btn.pack(pady=2)

        # Label statut connexion
        self.connection_label = ttk.Label(
            cookie_btn_frame, textvariable=self.connection_status_var, foreground="gray"
        )
        self.connection_label.pack(pady=2)

        # === SECTION CHARGEMENT ===
        # Séparateur
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10
        )

        # Bouton Charger
        self.load_btn = ttk.Button(
            main_frame, text="Charger mon emploi du temps", command=self._load_timetable
        )
        self.load_btn.grid(row=10, column=0, columnspan=3, pady=20)

        # Barre de statut
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(status_frame, text="Statut:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))

        # Treeview pour afficher les cours
        self._create_treeview(main_frame)

    def _create_treeview(self, parent):
        """Crée le Treeview pour afficher les cours."""

        # Frame pour le Treeview
        tree_frame = ttk.LabelFrame(parent, text="Emploi du temps", padding="5")
        tree_frame.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Colonnes du Treeview
        columns = ("jour", "horaire", "titre", "prof", "salle")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        # Configuration des en-têtes
        self.tree.heading("jour", text="Jour")
        self.tree.heading("horaire", text="Horaire")
        self.tree.heading("titre", text="Cours")
        self.tree.heading("prof", text="Professeur")
        self.tree.heading("salle", text="Salle")

        # Configuration des colonnes
        self.tree.column("jour", width=150, minwidth=100)
        self.tree.column("horaire", width=120, minwidth=80)
        self.tree.column("titre", width=200, minwidth=150)
        self.tree.column("prof", width=150, minwidth=100)
        self.tree.column("salle", width=100, minwidth=80)

        # Scrollbars
        tree_scroll_v = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scroll_h = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)

        # Placement
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_h.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def _setup_layout(self):
        """Configure la mise en page responsive."""

        # Configurer le redimensionnement
        for i in range(14):
            if i in [12]:  # Ligne du Treeview
                self.root.grid_rowconfigure(i, weight=1)

    def _test_connection(self):
        """Teste la connexion avec les cookies fournis."""

        url = self.url_var.get().strip()
        cookie = self.cookie_text.get(1.0, tk.END).strip()

        # Validation des champs
        if not url or not url.startswith("http"):
            messagebox.showerror("Erreur", "Veuillez saisir une URL valide")
            return

        if not cookie:
            messagebox.showerror("Erreur", "Veuillez coller vos cookies depuis Chrome")
            return

        # Lancer le test dans un thread séparé
        self._start_connection_test()
        thread = threading.Thread(target=self._test_connection_thread, args=(url, cookie))
        thread.daemon = True
        thread.start()

    def _start_connection_test(self):
        """Démarre l'indicateur de test de connexion."""
        self.test_btn.configure(state="disabled")
        self.connection_status_var.set("Test en cours...")
        self.connection_label.configure(foreground="orange")
        logger.info("Début du test de connexion")

    def _stop_connection_test(self):
        """Arrête l'indicateur de test de connexion."""
        self.test_btn.configure(state="normal")

    def _test_connection_thread(self, url: str, cookie: str):
        """Thread pour tester la connexion sans bloquer l'interface."""

        try:
            # Construire la session à partir des cookies
            session = build_session_from_cookie_header(cookie)

            # Tester l'authentification
            is_auth = is_authenticated(session, url)

            if is_auth:
                # Stocker la session pour réutilisation
                self.session = session
                self.root.after(0, self._update_connection_status, True, "✅ Connecté")
            else:
                self.session = None
                self.root.after(0, self._update_connection_status, False, "❌ Échec")

        except Exception as e:
            error_msg = f"❌ Erreur: {str(e)}"
            logger.error(f"Erreur lors du test de connexion: {e}")
            self.session = None
            self.root.after(0, self._update_connection_status, False, error_msg)

    def _update_connection_status(self, success: bool, message: str):
        """Met à jour le statut de connexion."""

        self._stop_connection_test()
        self.connection_status_var.set(message)

        if success:
            self.connection_label.configure(foreground="green")
            logger.info("Test de connexion réussi - session stockée")
        else:
            self.connection_label.configure(foreground="red")
            logger.warning("Test de connexion échoué")

    def _login_with_credentials(self):
        """Se connecter avec identifiant et mot de passe."""

        url = self.url_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # Validation des champs
        if not url or not url.startswith("http"):
            messagebox.showerror("Erreur", "Veuillez saisir une URL valide")
            return

        if not username:
            messagebox.showerror("Erreur", "Veuillez saisir votre identifiant")
            return

        if not password:
            messagebox.showerror("Erreur", "Veuillez saisir votre mot de passe")
            return

        # Lancer la connexion dans un thread séparé
        self._start_login()
        thread = threading.Thread(target=self._login_thread, args=(username, password, url))
        thread.daemon = True
        thread.start()

    def _start_login(self):
        """Démarre l'indicateur de connexion."""
        self.login_btn.configure(state="disabled")
        self.login_status_var.set("Connexion en cours...")
        self.login_status_label.configure(foreground="orange")
        logger.info("Début de la connexion avec identifiants")

    def _stop_login(self):
        """Arrête l'indicateur de connexion."""
        self.login_btn.configure(state="normal")

    def _login_thread(self, username: str, password: str, url: str):
        """Thread pour la connexion sans bloquer l'interface."""

        try:
            # Importer la fonction de connexion
            from src.wigor_api import login_with_credentials

            # Tenter la connexion
            result = login_with_credentials(username, password, url)

            if result["success"]:
                # Stocker la session pour réutilisation
                self.session = result["session"]

                # Remplir automatiquement le champ cookie
                cookies_str = result["cookies_string"]

                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, self._update_login_success, cookies_str)
            else:
                error_msg = result.get("error", "Erreur de connexion inconnue")
                status_code = result.get("status_code", "N/A")
                self.root.after(0, self._update_login_failure, error_msg, status_code)

        except Exception as e:
            error_msg = f"Erreur lors de la connexion: {str(e)}"
            logger.error(error_msg)
            self.root.after(0, self._update_login_failure, error_msg, "Exception")

    def _update_login_success(self, cookies_string: str):
        """Met à jour l'interface après connexion réussie."""

        self._stop_login()
        self.login_status_var.set("Connecté ✅")
        self.login_status_label.configure(foreground="green")

        # Remplir automatiquement le champ cookie
        self.cookie_text.delete(1.0, tk.END)
        self.cookie_text.insert(1.0, cookies_string)

        # Mettre à jour le statut de connexion cookie
        self.connection_status_var.set("✅ Session active")
        self.connection_label.configure(foreground="green")

        logger.info("Connexion avec identifiants réussie - cookies remplis automatiquement")
        messagebox.showinfo(
            "Succès", "Connexion réussie ! Les cookies ont été remplis automatiquement."
        )

    def _update_login_failure(self, error_msg: str, status_code: str):
        """Met à jour l'interface après échec de connexion."""

        self._stop_login()
        self.login_status_var.set(f"Échec de connexion ❌")
        self.login_status_label.configure(foreground="red")

        # Mettre à jour la barre de statut avec le code HTTP
        self.status_var.set(f"Erreur connexion - Code: {status_code}")

        logger.warning(f"Échec de connexion avec identifiants: {error_msg}")
        messagebox.showerror(
            "Échec de connexion", f"Impossible de se connecter:\n{error_msg}\n\nCode: {status_code}"
        )

    def _load_timetable(self):
        """Charge l'emploi du temps depuis Wigor."""

        url = self.url_var.get().strip()
        cookie = self.cookie_text.get(1.0, tk.END).strip()

        # Validation des champs
        if not url or not url.startswith("http"):
            messagebox.showerror("Erreur", "Veuillez saisir une URL valide")
            return

        if not cookie:
            messagebox.showerror("Erreur", "Veuillez coller vos cookies depuis Chrome")
            return

        # Vérifier si une session testée est disponible
        if self.session is not None:
            # Utiliser la session authentifiée
            logger.info("Utilisation de la session authentifiée existante")
            self._start_loading()
            thread = threading.Thread(target=self._fetch_data_with_session_thread, args=(url,))
            thread.daemon = True
            thread.start()
        else:
            # Pas de session testée, utiliser la méthode legacy
            logger.info("Aucune session testée, utilisation des cookies directs")
            self._start_loading()
            thread = threading.Thread(target=self._fetch_data_thread, args=(url, cookie))
            thread.daemon = True
            thread.start()

    def _start_loading(self):
        """Démarre l'indicateur de chargement."""
        self.load_btn.configure(state="disabled")
        self.status_var.set("Chargement en cours...")
        logger.info("Début du chargement de l'emploi du temps")

    def _stop_loading(self):
        """Arrête l'indicateur de chargement."""
        self.load_btn.configure(state="normal")

    def _fetch_data_thread(self, url: str, cookie: str):
        """Thread pour récupérer les données sans bloquer l'interface (méthode legacy)."""

        try:
            # Récupérer le HTML avec cookies
            html_content = fetch_wigor_html(url, cookie)

            # Parser les cours
            courses = parse_wigor_html(html_content)

            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, self._update_ui_with_data, courses, len(html_content))

        except Exception as e:
            error_msg = f"Erreur lors du chargement: {str(e)}"
            logger.error(error_msg)
            self.root.after(
                0,
                lambda: (
                    self._stop_loading(),
                    self.status_var.set("❌ Erreur de chargement"),
                    messagebox.showerror("Erreur", error_msg),
                ),
            )

    def _fetch_data_with_session_thread(self, url: str):
        """Thread pour récupérer les données avec une session authentifiée."""

        try:
            # Récupérer le HTML avec la session authentifiée
            html_content = fetch_wigor_html(url, session=self.session)

            # Parser les cours
            courses = parse_wigor_html(html_content)

            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, self._update_ui_with_data, courses, len(html_content))

        except Exception as e:
            error_msg = f"Erreur lors du chargement avec session: {str(e)}"
            logger.error(error_msg)
            # Si erreur avec session, réessayer sans session
            logger.info("Tentative de rechargement sans session")
            cookie = self.cookie_text.get(1.0, tk.END).strip()
            self._fetch_data_thread(url, cookie)

    def _update_ui_with_data(self, courses: List[Dict[str, str]], html_size: int):
        """Met à jour l'interface avec les données chargées."""

        self._stop_loading()
        self.courses_data = courses

        # Vider le Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ajouter les cours au Treeview
        for course in courses:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    course.get("jour", ""),
                    course.get("horaire", ""),
                    course.get("titre", ""),
                    course.get("prof", ""),
                    course.get("salle", ""),
                ),
            )

        # Mettre à jour le statut
        self.status_var.set(f"✅ {len(courses)} cours trouvés")

        logger.info(f"Interface mise à jour avec {len(courses)} cours")

    def run(self):
        """Lance l'application."""
        logger.info("Démarrage de l'interface graphique")
        self.root.mainloop()


def main():
    """Fonction principale pour lancer l'application."""

    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        app = WigorViewerGUI()
        app.run()
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'application: {e}")
        messagebox.showerror("Erreur fatale", f"Impossible de lancer l'application:\n{e}")


if __name__ == "__main__":
    main()
