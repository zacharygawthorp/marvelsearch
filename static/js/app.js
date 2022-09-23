function spinnerFunction() {
  const myVar = setTimeout(showPage, 1000);
  return myVar;
}

function showPage() {
  document.getElementById("loading").style.display = "none";
  document.getElementById("spinner").style.display = "none";
  document.getElementById("content").style.display = "block";
}
