$("select")
  .on("change", function() {
    $("select option:selected").val((index, value) => {
      const [card, currency] = value.split('-');
      $("#amount_label").text(`Amount in ${currency}`)
      $("#selectionId").attr("value", card)
      console.log(`${card} == ${currency}`);
    });
  });
