function autopopulateCelebrityStatus(){
  let celebrity = document.getElementsByName('celebrity');
  let celebrity_status = document.getElementById('celebrity_status').value;
  if (celebrity_status == 'yes'){
    celebrity[0].checked = true;
  } else{
    celebrity[1].checked = true;
  }
}

function autopopulateThemeSelection(){
  let themeSelect = document.getElementById('theme');
  let current_theme = document.getElementById('current_theme').value;
  themeSelect.value = current_theme;
}

function accountDeletionConfirmation(){
  if (confirm("                                           Are you sure?\nDeleting your account will also delete all of your posts and comments.")){
    window.location.href = '/delete_user';
  }
}

autopopulateCelebrityStatus();
autopopulateThemeSelection();
