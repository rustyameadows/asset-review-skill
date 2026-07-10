(() => {
  "use strict";

  const filter = document.querySelector("#asset-filter");
  const cards = [...document.querySelectorAll(".asset-card")];
  const groups = [...document.querySelectorAll(".asset-group")];
  const status = document.querySelector("#filter-status");

  if (filter && cards.length) {
    filter.addEventListener("input", () => {
      const query = filter.value.trim().toLocaleLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const matches = !query || card.textContent.toLocaleLowerCase().includes(query);
        card.hidden = !matches;
        if (matches) visible += 1;
      });
      groups.forEach((group) => {
        group.hidden = !group.querySelector(".asset-card:not([hidden])");
      });
      if (status) status.textContent = query ? `${visible} of ${cards.length} assets shown` : `${cards.length} assets`;
    });
    if (status) status.textContent = `${cards.length} assets`;
  }

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
