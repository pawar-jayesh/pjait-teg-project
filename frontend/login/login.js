import { BACKEND_URL } from "./../shared.js"

const btnLogin = document.querySelector('.login__btn');
const email = document.getElementById("email");


btnLogin.addEventListener('click', function (e) {
    // Prevent form from submitting
    e.preventDefault();
    if(email.value){
        fetch(`${BACKEND_URL}checkemail?email=${email.value}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Accept' : '*/*',
            }
            })
            .then(response => {
                if(!response.ok){
                    throw new Error(errorMessage + " " + response.status);
                }
                return response.json();
            })
            .then(data => {
                if(data["response"] == "Success"){
                    localStorage.setItem("email", email.value);
                    window.location.href = window.location.origin + "/frontend/chatbot/chatbot.html";
                } else {
                    alert(data["response"]);
                }
        })
    }
    else {
        alert("Please enter an email")
    }
});
