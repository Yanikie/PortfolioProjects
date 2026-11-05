(() => {
  const ENDPOINT = "/PHP/sendMail.php";
  const form = document.getElementById("contactForm");
  const note = document.getElementById("formNote");
  const button = form.querySelector("button");

  function showNote(message, isError = false) {
    note.textContent = message;
    note.classList.toggle("is-error", isError);
  }

  // -------- CSRF token --------
  async function loadToken() {
    const res = await fetch(`${ENDPOINT}?csrf=1`, { credentials: "same-origin" });
    const data = await res.json();

    let input = form.querySelector('input[name="csrf_token"]');
    if (!input) {
      input = document.createElement("input");
      input.type = "hidden";
      input.name = "csrf_token";
      form.appendChild(input);
    }
    input.value = data.token;
  }

  loadToken().catch(() => {
    showNote("The form couldn't load. Refresh the page, or email me at yannick@hogetoorn.com.", true);
  });

  // -------- Result from a non-JS submit --------
  const mail = new URLSearchParams(location.search).get("mail");
  if (mail === "success") showNote("Message sent. I'll get back to you soon.");
  if (mail === "failed") showNote("Message not sent. Try again, or email me at yannick@hogetoorn.com.", true);

  // -------- Submit --------
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showNote("");
    button.disabled = true;
    button.textContent = "Sending…";

    try {
      const res = await fetch(ENDPOINT, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form),
        credentials: "same-origin",
      });

      let result;
      try {
        result = await res.json();
      } catch {
        throw new Error("The server sent an unexpected response.");
      }

      if (!res.ok || !result.success) {
        throw new Error(result.error || result.message || "The server reported an error.");
      }

      form.reset();
      showNote("Message sent. I'll get back to you soon.");
    } catch (err) {
      showNote(`Message not sent. ${err.message} You can also email me at yannick@hogetoorn.com.`, true);
    } finally {
      button.disabled = false;
      button.textContent = "Send message";
      // The token is single-use, so fetch a fresh one for the next message
      loadToken().catch(() => {});
    }
  });
})();
