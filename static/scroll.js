        // Ширина одного элемента
        const scrollAmount =  document.querySelector('.previews').clientWidth;


        document.querySelectorAll('.content').forEach(function(container,index) {
            let text = container.querySelector('.content-text');
            let pics = container.querySelector('.previews');
            pics.setAttribute('data-scroll-direction',1);
            //pics.setAttribute('current-page',0);
            let picAmount = pics.children.length;
            let refNode = pics.nextSibling;
            for(let i = 0; i<picAmount;i++)
            {
                let radioInput = document.createElement('input');
                radioInput.type = 'radio';
                radioInput.name = `${index}`;
                radioInput.value = `${i}`;
                if (i==0)
                {
                    radioInput.checked=true;
                }
                radioInput.addEventListener('change',()=>{
                    if (radioInput.checked){
                        pics.scrollLeft=i*scrollAmount;
                    }
                });
                container.insertBefore(radioInput,refNode.nextSibling);
                refNode=radioInput;
            }
            
        });

document.querySelectorAll('.previews').forEach(function(container) {
    container.addEventListener('click', function() {
        let scroldir = parseInt(container.getAttribute('data-scroll-direction'));
        let parentChildren = Array.from(container.parentNode.children);
        if(container.scrollLeft%container.clientWidth!=0)
        {
            let compensate = Math.round(container.scrollLeft/container.clientWidth)*container.clientWidth
            container.scrollLeft=compensate;
            parentChildren[1+(compensate)/container.clientWidth].checked=true;
            return;
        }
        
        if (container.scrollLeft >= (container.scrollWidth - container.clientWidth))
        {
            scroldir=-1;
            container.setAttribute('data-scroll-direction', scroldir);
        }
        if(container.scrollLeft==0)
        {
            scroldir=1;
            container.setAttribute('data-scroll-direction', scroldir);
        }
        
        
        parentChildren[1+(container.scrollLeft+scrollAmount*scroldir)/container.clientWidth].checked=true;
        container.scrollLeft+=container.clientWidth*scroldir;
        
        

    });
});