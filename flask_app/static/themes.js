function themePicker(){
  let theme = document.getElementById('current_theme').value;
  console.log(theme);
  let link = document.getElementById('bootstrap_stylesheet');
  // link.href = "{{url_for('.static', filename='default.bootstrap.min.css')}}";
  link.href = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css";
}

// themePicker();

