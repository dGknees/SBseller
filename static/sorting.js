//оно не сделано
document.getElementById('sort').addEventListener('click',sort);

function sort()
{
    content = document.querySelectorAll(".content");
    content[0].style.order=5;
    content.forEach((item) => {
        item.classList.add('active');
      });

      setTimeout(() => {
        content.forEach((item) => {
          item.classList.remove('active');
        });
      }, 500);

    
}