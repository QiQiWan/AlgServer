function addCategory() {
    var keyword = $('#search-input').val();


    // 创建标签元素
    var tag = $('<span class="tag is-warning is-small"></span>').text(keyword);

    // 添加分类属性

    // 创建删除按钮
    var deleteBtn = $('<button>&times;</button>');
    deleteBtn.addClass("delete is-small");
    deleteBtn.click(function () {
        $(this).parent().remove();
    });

    // 将标签和删除按钮添加到显示区域
    tag.append(deleteBtn);
    $('#categoryTags').append(tag);

    // 清空输入框的值
    $('#search-input').val('');

    // 关闭模态框
    $('#addCategoryModal').modal('hide');
}


const searchInput = document.getElementById('search-input');
const autocompleteList = document.getElementById('autocomplete-list');

// 模拟的关键词数据源
const keywords = ['苹果', '香蕉', '橙子', '葡萄', '西瓜', '菠萝', '苹果派'];

searchInput.addEventListener('input', () => {
    const inputText = searchInput.value.trim();

    // 清空自动补全列表
    autocompleteList.innerHTML = '';

    if (inputText) {
        const matchingKeywords = keywords.filter(keyword =>
            keyword.toLowerCase().includes(inputText.toLowerCase())
        );

        matchingKeywords.forEach(keyword => {
            const li = document.createElement('li');
            li.textContent = keyword;
            autocompleteList.appendChild(li);
        });
    }
});

autocompleteList.addEventListener('click', event => {
    if (event.target.tagName === 'LI') {
        searchInput.value = event.target.textContent;
        autocompleteList.innerHTML = '';
    }
});