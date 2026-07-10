(() => {
  "use strict";

  const backgroundButtons = [...document.querySelectorAll("[data-background]")];
  const stages = [...document.querySelectorAll(".focus-stage, .comparison-stage")];
  backgroundButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const background = button.dataset.background;
      stages.forEach((stage) => {
        stage.classList.remove("checker", "black", "white");
        stage.classList.add(background);
      });
      backgroundButtons.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
    });
  });
})();
