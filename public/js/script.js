(function(document) {
  var toggle = document.querySelector('.sidebar-toggle');
  var sidebar = document.querySelector('#sidebar');
  var checkbox = document.querySelector('#sidebar-checkbox');

  toggle.addEventListener('click', function(e) {
    e.preventDefault();  //prevents page from scrolling to the top on click of the toggle button
    checkbox.checked = !checkbox.checked;
  });

  document.addEventListener('click', function(e) {
    var target = e.target;

    if(!checkbox.checked ||
       sidebar.contains(target) ||
       (target === checkbox || target === toggle)) return;

    checkbox.checked = false;
  }, false);
})(document);

// Code for collabsible sidebar menu
document.addEventListener("DOMContentLoaded", function() {

  function scrollToAnchor() {
    var hash = window.location.hash;
    if (hash) {
      var target = document.querySelector(hash);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }

  scrollToAnchor(); //scrolls to ankchor in url on page load

  // Scroll to anchor on URL change
  window.addEventListener('hashchange', function() {
    scrollToAnchor();
  });

  var coll = document.getElementsByClassName("collapsible");
  for (var i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
      this.classList.toggle("active");
      var content = this.nextElementSibling;
      if (content.style.display === "block") {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    });
  }
});
