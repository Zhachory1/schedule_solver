const schema = {
    "components": [
      {
        "label": "Task Name",
        "type": "textfield",
        "id": "Field_0gwgd6n",
        "key": "name"
      },
      {
        "label": "Task Description",
        "type": "textfield",
        "id": "Field_1jwtdy0",
        "key": "description"
      },
      {
        "label": "Priority",
        "type": "number",
        "id": "Field_0da4294",
        "key": "priority"
      },
      {
        "label": "Hours to complete",
        "type": "number",
        "id": "Field_0v2waog",
        "key": "hours"
      }
    ],
    "type": "default",
    "id": "Form_0ir370i",
    "exporter": {
      "name": "form-js (https://demo.bpmn.io)",
      "version": "0.7.2"
    },
    "schemaVersion": 4
  };

const container = document.querySelector('#inputs');

let form = FormViewer.createForm({
    container,
    schema
});

// form.on('submit', (event) => {
//     console.log(event.data, event.errors);
// });

function onStartup() {
}

onStartup();