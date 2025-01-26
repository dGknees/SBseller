const nametags = document.querySelectorAll('.nametag');
function checkOverflows(){
    nametags.forEach(function (nametag) {
        if (nametag.scrollWidth > nametag.clientWidth) {
          nametag.classList.add('overflow');
        } else {
          nametag.classList.remove('overflow');
        }
      });
}

checkOverflows();

window.addEventListener('resize', checkOverflows);