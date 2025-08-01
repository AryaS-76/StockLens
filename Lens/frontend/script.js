let selectedScore = null;

function selectOption(score) {
  selectedScore = score;
  document.querySelectorAll('.option-card').forEach(el => {
    el.classList.remove('selected');
  });
  event.currentTarget.classList.add('selected');
}

function goToNext() {
  if (selectedScore === null) {
    alert("Please select an option to continue.");
    return;
  }

  localStorage.setItem("q1_age", selectedScore);
  window.location.href = "question2.html";  // We'll create this later
}
