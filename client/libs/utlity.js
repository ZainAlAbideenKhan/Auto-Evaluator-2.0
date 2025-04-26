document.querySelectorAll(".input-container").forEach(function (ele) {
  ele.querySelector(".input").addEventListener("focusin", () => {
    ele.querySelector(".label").classList.add("label-focused");
  });
  ele.querySelector(".input").addEventListener("focusout", () => {
    if (ele.querySelector(".input").value == "")
      ele.querySelector(".label").classList.remove("label-focused");
  });
});

document.querySelector(".theme-btn-container").addEventListener("click", () => {
  if (document.body.classList.contains("dark")) {
    document.body.classList.remove("dark");
    document.body.classList.add("light");
  } else {
    document.body.classList.remove("light");
    document.body.classList.add("dark");
  }
});
