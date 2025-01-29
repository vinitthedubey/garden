// Firebase configuration (replace with your credentials)
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

document.getElementById("google-login").addEventListener("click", () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then((result) => {
            window.location.href = `/google-login?email=${result.user.email}&name=${result.user.displayName}`;
        })
        .catch((error) => {
            console.error("Error logging in with Google:", error);
        });
});

document.getElementById("google-register").addEventListener("click", () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then((result) => {
            window.location.href = `/google-register?email=${result.user.email}&name=${result.user.displayName}`;
        })
        .catch((error) => {
            console.error("Error registering with Google:", error);
        });
});
