from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import DepotAudio


class PagesTests(TestCase):
    def test_accueil_affiche_formulaire_de_depot(self):
        utilisateur = User.objects.create_user(username="musicien", password="test-password-123")
        self.client.force_login(utilisateur)

        response = self.client.get(reverse("accueil"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enctype="multipart/form-data"')

    def test_accueil_redirige_vers_connexion_si_deconnecte(self):
        response = self.client.get(reverse("accueil"))

        self.assertRedirects(
            response,
            f"{reverse('connexion')}?next={reverse('accueil')}",
        )

    def test_depot_audio_affiche_resultat_demo_sans_transformation(self):
        utilisateur = User.objects.create_user(username="musicien", password="test-password-123")
        self.client.force_login(utilisateur)
        audio = SimpleUploadedFile("morceau.mp3", b"audio de test", content_type="audio/mpeg")

        response = self.client.post(
            reverse("resultat"),
            {"audio": audio},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "morceau.mp3")
        self.assertContains(response, "n’est pas encore activée")
        self.assertEqual(DepotAudio.objects.count(), 1)

    def test_historique_affiche_nom_date_et_lien_vers_resultat(self):
        utilisateur = User.objects.create_user(username="musicien", password="test-password-123")
        depot = DepotAudio.objects.create(
            utilisateur=utilisateur,
            nom_fichier="sonate.mp3",
        )
        self.client.force_login(utilisateur)

        response = self.client.get(reverse("historique"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sonate.mp3")
        self.assertContains(response, depot.date_depot.strftime("%d/%m/%Y"))
        self.assertContains(response, reverse("resultat-detail", args=[depot.id]))
        self.assertContains(response, 'class="nav-button" href="/"')
        self.assertContains(response, 'class="nav-button" href="/historique/"')
        self.assertNotContains(response, ">Retour à l’accueil</a>")

    def test_resultat_et_pdf_sont_limites_au_proprietaire(self):
        proprietaire = User.objects.create_user(username="proprietaire", password="test-password-123")
        autre = User.objects.create_user(username="autre", password="test-password-123")
        depot = DepotAudio.objects.create(
            utilisateur=proprietaire,
            nom_fichier="morceau.mp3",
        )
        self.client.force_login(autre)

        self.assertEqual(
            self.client.get(reverse("resultat-detail", args=[depot.id])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("telecharger-partition", args=[depot.id])).status_code,
            404,
        )

    def test_telechargement_renvoie_un_pdf_de_demo(self):
        utilisateur = User.objects.create_user(username="musicien", password="test-password-123")
        depot = DepotAudio.objects.create(
            utilisateur=utilisateur,
            nom_fichier="morceau.mp3",
        )
        self.client.force_login(utilisateur)

        response = self.client.get(
            reverse("telecharger-partition", args=[depot.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF-1.4"))
        self.assertIn(b"pas la transcription du fichier", response.content)

    def test_depot_refuse_extension_non_audio(self):
        utilisateur = User.objects.create_user(username="musicien", password="test-password-123")
        self.client.force_login(utilisateur)
        fichier = SimpleUploadedFile("document.txt", b"texte")

        response = self.client.post(reverse("resultat"), {"audio": fichier})

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "fichier audio accepté", status_code=400)

    def test_connexion_et_deconnexion(self):
        utilisateur = User(username="musicien")
        utilisateur.set_password("test-password-123")
        utilisateur.save()

        response = self.client.post(
            reverse("connexion"),
            {"username": "musicien", "password": "test-password-123"},
        )

        self.assertRedirects(response, reverse("accueil"))
        self.assertIn("_auth_user_id", self.client.session)

        response = self.client.post(reverse("deconnexion"))

        self.assertRedirects(response, reverse("connexion"))
        self.assertNotIn("_auth_user_id", self.client.session)
