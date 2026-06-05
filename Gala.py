import pandas as pd
import streamlit as st


PRICES_FILE = "Prix gala.xlsx"

st.set_page_config(page_title="Caisse Gala", page_icon="🍹", layout="wide")

st.markdown(
    """
    <style>
        .big-title {
            font-size: 45px;
            font-weight: 900;
            text-align: center;
            color: #ff4b4b;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: grey;
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 28px;
            font-weight: 800;
            margin-top: 10px;
        }
        .ticket-box {
            padding: 20px;
            border-radius: 18px;
            background-color: #f7f7f7;
            margin-bottom: 20px;
        }

        div[data-testid="stButton"] > button {
            font-weight: bold;
            border-radius: 15px;
            min-height: 50px;
            border: none;
            white-space: pre-line;
        }

        div[data-testid="stButton"] > button[kind="secondary"] {
            background-color: #4da6ff;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">🍹 Caisse Gala de Danse 💃</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Clique sur un article pour l\'ajouter à la commande</div>',
    unsafe_allow_html=True,
)


@st.cache_data
def charger_prix() -> pd.DataFrame:
    return pd.read_excel(PRICES_FILE)


df = charger_prix()

colonnes_attendues = ["Catégories", "Articles", "Prix"]
for col in colonnes_attendues:
    if col not in df.columns:
        st.error(f"Ton fichier Excel doit contenir la colonne : '{col}'")
        st.stop()

df_boisson = df[df["Catégories"] == "Boisson"]
df_encas = df[df["Catégories"] == "Encas"]
df_consigne = df[df["Catégories"] == "Consigne"]

if "commande" not in st.session_state:
    st.session_state.commande = {}

if "consignes" not in st.session_state:
    st.session_state.consignes = {}


def ajouter_article(article: str) -> None:
    st.session_state.commande[article] = st.session_state.commande.get(article, 0) + 1


def retirer_article(article: str) -> None:
    if article in st.session_state.commande:
        st.session_state.commande[article] -= 1
        if st.session_state.commande[article] <= 0:
            del st.session_state.commande[article]


def ajouter_consigne(article: str) -> None:
    st.session_state.consignes[article] = st.session_state.consignes.get(article, 0) + 1


def retour_consigne(article: str) -> None:
    if article in st.session_state.consignes:
        st.session_state.consignes[article] -= 1
        if st.session_state.consignes[article] <= 0:
            del st.session_state.consignes[article]


def reset_commande() -> None:
    st.session_state.commande = {}
    st.session_state.consignes = {}


def afficher_menu(df_menu: pd.DataFrame, nb_max_colonnes: int = 3) -> None:
    nb_items = len(df_menu)

    if nb_items == 0:
        st.warning("Aucun article trouvé.")
        return

    nb_colonnes = min(nb_items, nb_max_colonnes)
    cols = st.columns(nb_colonnes)

    for index, row in enumerate(df_menu.itertuples(index=False)):
        article = row.Articles
        prix = float(row.Prix)

        with cols[index % nb_colonnes]:
            if st.button(
                f"{article}\n💰 {prix:.2f} €",
                use_container_width=True,
                key=f"article_{article}",
            ):
                ajouter_article(article)
                st.rerun()


col_menu, col_ticket = st.columns([2, 1])

with col_menu:
    st.markdown('<div class="section-title">🥤 Boissons</div>', unsafe_allow_html=True)
    afficher_menu(df_boisson)

    st.markdown("---")

    st.markdown('<div class="section-title">🍟 Encas</div>', unsafe_allow_html=True)
    afficher_menu(df_encas)

    st.markdown("---")

    st.markdown('<div class="section-title">♻️ Consignes</div>', unsafe_allow_html=True)

    if df_consigne.empty:
        st.info("Aucune consigne trouvée dans ton Excel.")
    else:
        for row in df_consigne.itertuples(index=False):
            article = row.Articles
            prix = float(row.Prix)

            c1, c2, c3 = st.columns([2, 2, 2])

            with c1:
                st.write(f"{article} ({prix:.2f} €)")

            with c2:
                if st.button("➕ Ajouter", key=f"add_cons_{article}", use_container_width=True):
                    ajouter_consigne(article)
                    st.rerun()

            with c3:
                if st.button("➖ Retour", key=f"remove_cons_{article}", use_container_width=True):
                    retour_consigne(article)
                    st.rerun()

with col_ticket:
    st.subheader("🧾 Ticket")

    if len(st.session_state.commande) == 0 and len(st.session_state.consignes) == 0:
        st.info("Aucune commande en cours.")
    else:
        total = 0.0

        st.markdown('<div class="ticket-box">', unsafe_allow_html=True)

        if len(st.session_state.commande) > 0:
            st.markdown("### 🍽️ Articles")

            for article, quantite in st.session_state.commande.items():
                prix = float(df[df["Articles"] == article]["Prix"].values[0])
                sous_total = prix * quantite
                total += sous_total

                col_a, col_b, col_c = st.columns([3, 1, 1])

                with col_a:
                    st.write(f"**{article}** x{quantite}")

                with col_b:
                    st.write(f"{sous_total:.2f} €")

                with col_c:
                    if st.button("➖", key=f"remove_{article}"):
                        retirer_article(article)
                        st.rerun()

        if len(st.session_state.consignes) > 0:
            st.markdown("### ♻️ Consignes")

            for article, quantite in st.session_state.consignes.items():
                prix = float(df[df["Articles"] == article]["Prix"].values[0])
                sous_total = prix * quantite
                total += sous_total

                st.write(f"{article} x{quantite} → {sous_total:.2f} €")

        st.markdown("</div>", unsafe_allow_html=True)

        st.success(f"💰 Total à payer : **{total:.2f} €**")

        montant_donne = st.number_input("💵 Montant donné (€)", min_value=0.0, step=0.5)
        rendu = montant_donne - total

        if montant_donne > 0:
            if rendu < 0:
                st.error(f"❌ Il manque : {-rendu:.2f} €")
            else:
                st.info(f"✅ Monnaie à rendre : **{rendu:.2f} €**")

        st.markdown("---")

        if st.button("🗑️ Nouvelle commande", use_container_width=True):
            reset_commande()
            st.rerun()
