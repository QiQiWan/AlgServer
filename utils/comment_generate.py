from django.utils.safestring import mark_safe
import textwrap
import time


class Comment_generate(object):  # 用于生成回复评论的html
    def __init__(self, request, queryset):
        self.request = request
        self.queryset = queryset
        self.template = """
        <div id="recordTemplate">
        <div class="item clearfix" id="{id}" username="{user}">
            <div class="left-avatar">{avatarname}</div>
            <span>{commentuser} - - > {replyuser}</span>
            <div class="right-info">
                <pre>{content}</pre>
                <div class="desc">
                    <div class="msg">
                    <button>
                    <i class="fa fa-thumbs-up btn_comment_like" aria-hidden="true" id="{id}" type="Comment_Reply">
                        <span id="likes">{likes}</span></i>
                    </button>                    
                    </div>
                    <div class="msg">
                        <i class="fa fa-clock-o" aria-hidden="true"></i>
                        <span class="date">{time}</span>
                    </div>
                    <div class="msg">
                        <button class="toggleButton">
                            <i class="fa fa-commenting-o" aria-hidden="true"></i> 回复
                        </button>
                    </div>
                    <div class="inputContainer" style="display: none;">
                    <form class="reply_form" id="{commentid}" type="{id}" user="{userid}"> 
                        <input class="input is-success" id="reply_content" type="text" placeholder="在此输入回复......">
                        <input class="button is-primary reply" id="{id}"  type="button" value="回 复">

                    </form>
                    </div>
                </div>
            </div>
        </div>
        <div class="comment_reply_container" id="{id}"></div>
    </div>
    
    """

    @property
    def html(self):
        html_string = ""
        for item in self.queryset:
            formatted_message = textwrap.dedent(self.template).format(
                avatarname=item.user.username[0],
                user=item.user.username,
                replyuser=item.reply_user.username,
                commentuser=item.user.username,
                content=item.content,
                likes=item.likes,
                time=item.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                id=item.id,
                commentid=item.comment.id,
                userid=item.user.id,
            )
            html_string += formatted_message
        html_string_safe = mark_safe("".join(html_string))
        return html_string_safe


# class main_comment_generate(object):  # 用于生成主评论的html（此处用bulma中css框架的评论）
#     def __init__(self, request, comment_object):
#         self.comment = comment_object
#         self.template = """
#        <article class="media">
#   <figure class="media-left">
#     <p class="image is-64x64">
#       <img src="https://bulma.io/images/placeholders/128x128.png">
#     </p>
#   </figure>
#   <div class="media-content">
#     <div class="content">
#       <p>
#         <strong>{username}</strong>
#         <br>
#        {content}
#       </p>
#     </div>
#     <nav class="level is-mobile">
#       <div class="level-left">
#         <a class="level-item">
#           <span class="icon is-small"><i class="fas fa-reply"></i></span>
#         </a>
#         <a class="level-item">
#           <span class="icon is-small"><i class="fas fa-retweet"></i></span>
#         </a>
#         <a class="level-item">
#           <span class="icon is-small"><i class="fas fa-heart"></i></span>
#         </a>
#       </div>
#     </nav>
#   </div>
#   <div class="media-right">
#     <button class="delete"></button>
#   </div>
# </article>
#         """

#     @property
#     def html(self):
#         formatted_message = textwrap.dedent(self.template).format(
#             username=self.comment.user.username,
#             content=self.comment.content,
#         )
#         html_string_safe = mark_safe("".join(formatted_message))
#         return html_string_safe


if __name__ == "__main__":
    print(mark_safe("".join(Comment_generate(1, 1).template)))
