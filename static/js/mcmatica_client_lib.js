function fill_inputs_form(container_id, data) {
    console.log(container_id);
    console.log(data);
    console.log(document.getElementById(data).innerHTML);

    let json_data = JSON.parse(document.getElementById(data).innerHTML)

    for (let key in json_data) {
    // Trova l'elemento input con id uguale alla chiave del dizionario
    let inputElement = document.getElementById(key);

    // Se l'elemento esiste, aggiorna il suo valore
    if (inputElement) {
      inputElement.value = json_data[key];
    }
  }
}

function getContext(container_id) {
    console.log("getContext.container_id",container_id)
    console.log("getContext.document.getElementById(container_id).innerHTML",document.getElementById(container_id).innerHTML)
    let json_data = JSON.parse(document.getElementById(container_id).innerHTML)
    return json_data
}


