from django.conf import settings
import vk_api
vk_session = vk_api.VkApi(token=settings.VK_GROUP_TOKEN)


def send_vk_message(user_id: int, text: str):
    
    vk = vk_session.get_api()

    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=0 
    )