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
        async function addSkill(){
        const name = document.getElementById('new-skill-name').value;
        const section_id = document.getElementById('skill-section').value;

        const formData = new FormData();
        formData.append('name',name);
        formData.append('section_id',section_id);

        try{
            const response = await fetch('/api/add-skill/',{
                method:'POST',
                body:formData,
                headers:{
                    'X-CSRFToken':getCookie('csrftoken')
                }
                });
                const data = await response.json();
                if(data.status === 'success'){
                  alert('Skill added');
                  location.reload();
                }
        }catch (error){
            alert('Error');
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