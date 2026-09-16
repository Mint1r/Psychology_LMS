const purchaseErrorModal = document.getElementById('purchaseErrorModal');
const purchaseErrorClose = document.getElementById('purchaseErrorClose');
const purchaseErrorOk = document.getElementById('purchaseErrorOk');

function closePurchaseErrorModal() {
    if (purchaseErrorModal) {
        purchaseErrorModal.remove();
    }
}

if (purchaseErrorClose) {
    purchaseErrorClose.addEventListener(
        'click',
        closePurchaseErrorModal
    );
}

if (purchaseErrorOk) {
    purchaseErrorOk.addEventListener(
        'click',
        closePurchaseErrorModal
    );
}
