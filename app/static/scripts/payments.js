let [card, currency, usd_rate, blended_rate] = [null, null, null, null];
$("select")
  .on("change", function() {
    $("select option:selected").val((index, value) => {
      [card, currency, usd_rate, blended_rate] = value.split('-');
      $("#selectionId").attr("value", card)
      console.log(`${card} == ${currency}`);
    });
  });

$("input[name=amount]")
  .on("change", function() {
    const amt = $("input[name=amount]").val();
    if (card && currency && usd_rate) {
      const cardAmount = parseInt(amt) * parseFloat(usd_rate).toFixed(2)
      const kes_amt = parseInt(amt) * parseFloat(blended_rate).toFixed(2)
      $("small[id=amountHelp]").text(`${cardAmount} ${currency} -> ${kes_amt} KES.`)
    } else {
      $("small[id=amountHelp]").text(`${cardAmount} ${currency} -> ${kes_amt} KES.`)
    }
  });
