// Basic JavaScript for NOVAXA Dashboard

document.addEventListener("DOMContentLoaded", function () {
  console.log("NOVAXA Dashboard is ready");

  // Example dynamic project status loading
  fetch("/api/projects")
    .then(response => response.json())
    .then(data => {
      console.log("Projects loaded:", data);
      // TODO: Εμφάνιση projects στο frontend
    })
    .catch(error => console.error("Error loading projects:", error));
});
