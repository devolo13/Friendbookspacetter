post_id = document.getElementById('post_id').value

function postDeletionConfirmation(){
  if (confirm("Are you sure?")){
    window.location.href = '/delete_post/' + post_id;
  }
}
