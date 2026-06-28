// Community Hero — small UX helpers, no framework needed.

document.addEventListener("DOMContentLoaded", () => {
  // Auto-fade flash messages after a few seconds.
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.6s ease";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 700);
    }, 4000);
  });

  // Show the picked filename next to the media input on the composer.
  const mediaInput = document.getElementById("media-input");
  const mediaHint = document.getElementById("media-hint");
  if (mediaInput && mediaHint) {
    const defaultHint = mediaHint.textContent;
    mediaInput.addEventListener("change", () => {
      mediaHint.textContent = mediaInput.files.length
        ? `Selected: ${mediaInput.files[0].name}`
        : defaultHint;
    });
  }
});
