import pandas as pd
import streamlit as st


PRICES_FILE = "Prix gala.xlsx"

st.set_page_config(page_title="Caisse Gala", page_icon="€", layout="wide")

st.markdown(
    """
    <style>
        header[data-testid="stHeader"],
        #MainMenu,
        footer {
            display: none;
        }

        .block-container {
            padding-top: 0.6rem;
            padding-bottom: 0.7rem;
            padding-left: 0.7rem;
            padding-right: 0.7rem;
            max-width: 100%;
        }

        [data-testid="stVerticalBlock"] {
            gap: 0.45rem;
        }

        hr {
            margin: 0.55rem 0;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 800;
            margin: 0.1rem 0 0.25rem 0;
        }

        .ticket-box {
            padding: 0.7rem;
            border-radius: 8px;
            background-color: #f7f7f7;
            margin-bottom: 0.55rem;
        }

        div[data-testid="stButton"] > button {
            min-height: 3.25rem;
            border: 0;
            border-radius: 8px;
            font-weight: 800;
            line-height: 1.15;
            white-space: pre-line;
            transition: transform 120ms ease, filter 120ms ease, background-color 120ms ease;
        }

        div[data-testid="stButton"] > button:active {
            transform: scale(0.96);
            filter: brightness(1.2);
        }

        div[data-testid="stButton"] > button[kind="secondary"] {
            background-color: #1565c0;
            color: white;
        }

        div[data-testid="stButton"] > button[kind="secondary"]:hover {
            background-color: #0f7b52;
            color: white;
        }

        div[data-testid="stNumberInput"] label,
        div[data-testid="stTextInput"] label {
            font-weight: 700;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 0.25rem;
                padding-left: 0.45rem;
                padding-right: 0.45rem;
            }

            .section-title {
                font-size: 1rem;
            }

            div[data-testid="stButton"] > button {
                min-height: 2.9rem;
                padding: 0.25rem 0.35rem;
                font-size: 0.86rem;
            }
        }

        @media (orientation: landscape) and (max-height: 520px) {
            .block-container {
                padding-top: 0.2rem;
                padding-bottom: 0.2rem;
            }

            .section-title {
                font-size: 0.95rem;
                margin-bottom: 0.15rem;
            }

            div[data-testid="stButton"] > button {
                min-height: 2.45rem;
                font-size: 0.78rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def charger_prix() -> pd.DataFrame:
    return pd.read_excel(PRICES_FILE)


def format_euros(value: float) -> str:
    return f"{value:.2f} €"


def prix_article(article: str) -> float:
    return float(df.loc[df["Articles"] == article, "Prix"].iloc[0])


def parse_montant(value: str) -> float | None:
    value = value.strip().replace("€", "").replace(" ", "").replace(",", ".")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


df = charger_prix()

colonnes_attendues = ["Catégories", "Articles", "Prix"]
for col in colonnes_attendues:
    if col not in df.columns:
        st.error(f"Ton fichier Excel doit contenir la colonne : '{col}'")
        st.stop()

df = df.copy()
df["Prix"] = pd.to_numeric(df["Prix"], errors="coerce")
df = df.dropna(subset=["Prix"]).sort_values(["Prix", "Articles"], ascending=[True, True])

df_boisson = df[df["Catégories"] == "Boisson"]
df_encas = df[df["Catégories"] == "Encas"]
df_consigne = df[df["Catégories"] == "Consigne"]

if "commande" not in st.session_state:
    st.session_state.commande = {}

if "consignes" not in st.session_state:
    st.session_state.consignes = {}

if "last_action" not in st.session_state:
    st.session_state.last_action = None


def confirmer_action(message: str) -> None:
    st.session_state.last_action = message
    st.toast(message)


def ajouter_article(article: str) -> None:
    st.session_state.commande[article] = st.session_state.commande.get(article, 0) + 1
    confirmer_action(f"{article} ajouté")


def retirer_article(article: str) -> None:
    if article in st.session_state.commande:
        st.session_state.commande[article] -= 1
        if st.session_state.commande[article] <= 0:
            del st.session_state.commande[article]
        confirmer_action(f"{article} retiré")


def ajouter_consigne(article: str) -> None:
    st.session_state.consignes[article] = st.session_state.consignes.get(article, 0) + 1
    confirmer_action(f"{article} ajouté")


def retour_consigne(article: str) -> None:
    if article in st.session_state.consignes:
        st.session_state.consignes[article] -= 1
        if st.session_state.consignes[article] <= 0:
            del st.session_state.consignes[article]
        confirmer_action(f"{article} retourné")


def reset_commande() -> None:
    st.session_state.commande = {}
    st.session_state.consignes = {}
    confirmer_action("Nouvelle commande")


def afficher_menu(df_menu: pd.DataFrame, prefix: str, nb_max_colonnes: int = 3) -> None:
    nb_items = len(df_menu)

    if nb_items == 0:
        st.warning("Aucun article trouvé.")
        return

    nb_colonnes = min(nb_items, nb_max_colonnes)
    rows = list(df_menu.itertuples(index=False))
    for start in range(0, nb_items, nb_colonnes):
        cols = st.columns(nb_colonnes, gap="small")
        for offset, row in enumerate(rows[start : start + nb_colonnes]):
            article = row.Articles
            prix = float(row.Prix)

            with cols[offset]:
                if st.button(
                    f"{article}\n{format_euros(prix)}",
                    use_container_width=True,
                    key=f"{prefix}_{article}",
                ):
                    ajouter_article(article)
                    st.rerun()


col_menu, col_ticket = st.columns([2, 1], gap="small")

with col_menu:
    st.markdown('<div class="section-title">Boissons</div>', unsafe_allow_html=True)
    afficher_menu(df_boisson, "boisson")

    st.markdown("---")

    st.markdown('<div class="section-title">Encas</div>', unsafe_allow_html=True)
    afficher_menu(df_encas, "encas")

    st.markdown("---")

    st.markdown('<div class="section-title">Consignes</div>', unsafe_allow_html=True)

    if df_consigne.empty:
        st.info("Aucune consigne trouvée dans ton Excel.")
    else:
        for row in df_consigne.itertuples(index=False):
            article = row.Articles
            prix = float(row.Prix)

            c1, c2, c3 = st.columns([1.7, 1, 1], gap="small")

            with c1:
                st.write(f"**{article}**  {format_euros(prix)}")

            with c2:
                if st.button("+", key=f"add_cons_{article}", use_container_width=True):
                    ajouter_consigne(article)
                    st.rerun()

            with c3:
                if st.button("-", key=f"remove_cons_{article}", use_container_width=True):
                    retour_consigne(article)
                    st.rerun()

with col_ticket:
    st.subheader("Ticket")

    if st.session_state.last_action:
        st.caption(st.session_state.last_action)

    if len(st.session_state.commande) == 0 and len(st.session_state.consignes) == 0:
        st.info("Aucune commande en cours.")
    else:
        total = 0.0

        st.markdown('<div class="ticket-box">', unsafe_allow_html=True)

        if len(st.session_state.commande) > 0:
            st.markdown("#### Articles")

            for article, quantite in st.session_state.commande.items():
                prix = prix_article(article)
                sous_total = prix * quantite
                total += sous_total

                col_a, col_b, col_c = st.columns([2.4, 1, 0.7], gap="small")

                with col_a:
                    st.write(f"**{article}** x{quantite}")

                with col_b:
                    st.write(format_euros(sous_total))

                with col_c:
                    if st.button("-", key=f"remove_{article}", use_container_width=True):
                        retirer_article(article)
                        st.rerun()

        if len(st.session_state.consignes) > 0:
            st.markdown("#### Consignes")

            for article, quantite in st.session_state.consignes.items():
                prix = prix_article(article)
                sous_total = prix * quantite
                total += sous_total

                st.write(f"{article} x{quantite} -> {format_euros(sous_total)}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.success(f"Total à payer : **{format_euros(total)}**")

        montant_saisi = st.text_input(
            "Montant donné (€)",
            value="",
            placeholder="Ex : 20",
            key="montant_donne",
        )
        montant_donne = parse_montant(montant_saisi)

        if montant_saisi.strip():
            if montant_donne is None:
                st.error("Montant invalide")
            else:
                rendu = montant_donne - total
                if rendu < 0:
                    st.error(f"Il manque : {format_euros(-rendu)}")
                else:
                    st.info(f"Monnaie à rendre : **{format_euros(rendu)}**")

        st.markdown("---")

        if st.button("Nouvelle commande", use_container_width=True):
            reset_commande()
            st.rerun()
