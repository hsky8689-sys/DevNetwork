function getCookie(name){
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        async function goToProjectCreation(){
           try{
        const response = await fetch('/users/create-new-project/', {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const data = await response.json();
        if(data.status === 'success'){
            window.location.href = '/users/create-new-project/';  // Tot redirect
        }
    } catch(error) {
        window.location.href = '/users/create-new-project/';
    }
    }
    async function switchAccount(){
           try{
        const response = await fetch("/login/", {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const data = await response.json();
        if(data.status === 'success'){
            window.location.href = "/login/";  // Tot redirect
        }
    } catch(error) {
        window.location.href = '/login/';
    }
    }
        async function goToSearch(){
           try{
        const response = await fetch('/users/search/', {
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const data = await response.json();
        if(data.status === 'success'){
            window.location.href = '/users/search/';  // Tot redirect
        }
    } catch(error) {
        window.location.href = '/users/search/';
    }
    }
        async function addSkill(categoryId){
        const input = document.querySelector(`input[data-category-id="${categoryId}"]`);
        const name = input.value.trim();

        if(!name){
            alert('Scrie un skill');
            return;
        }
        const formData = new FormData();
        formData.append('name',name);
        formData.append('section_id',categoryId);

        try{
            const response = await fetch(`/users/api/add-skill/`,{
                method:'POST',
                body:formData,
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                }
            });

            const data = await response.json();
            if(data.status === 'success'){
                alert('Skill added to '+input.placeholder);
                input.value="";
                location.reload();
            }
        }catch (error){
            alert('Error: '+error)
        }
        }
        async function deleteSkill(skillId) {
            if (confirm('Ștergi skill-ul?')) {
                await fetch(`/api/delete-skill/${skillId}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCookie('csrftoken') }
            });
            location.reload();
        }
    }