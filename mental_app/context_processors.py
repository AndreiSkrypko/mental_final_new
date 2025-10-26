from .models import ClassGameAccess
from django.core.cache import cache
import json

# Константа для списка игр учителя (кешированная)
TEACHER_GAMES_LIST = [
    'multiplication_choose',
    'multiplication_to_20', 
    'square',
    'tricks',
    'flashcards',
    'multiplication_base',
    'brothers',
    'friends',
    'friend_brother',
    'multiplication_table'
]

def available_games(request):
    """
    ОПТИМИЗИРОВАННЫЙ контекстный процессор для определения доступных игр с кэшированием
    """
    available_games_list = []
    
    # Если это ученик (авторизован через сессию)
    student_id = request.session.get('student_id')
    if student_id:
        # ОПТИМИЗАЦИЯ: используем кэш для игр студента
        cache_key = f'student_games_{student_id}'
        cached_games = cache.get(cache_key)
        
        if cached_games is not None:
            available_games_list = cached_games
        else:
            try:
                from .models import Students
                # ОПТИМИЗАЦИЯ: используем select_related
                student = Students.objects.select_related('student_class').get(id=student_id)
                if student.student_class:
                    # Получаем игры, доступные для класса ученика
                    class_games = ClassGameAccess.objects.filter(
                        class_group=student.student_class,
                        is_enabled=True
                    ).values_list('game', flat=True)
                    available_games_list = list(class_games)
                    
                    # Кешируем результат на 5 минут
                    cache.set(cache_key, available_games_list, 300)
            except:
                pass
    
    # Если это учитель (авторизован через Django)
    elif hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved':
        # ОПТИМИЗАЦИЯ: используем кешированный список для учителей
        available_games_list = TEACHER_GAMES_LIST.copy()
    
    # Игра "simply" всегда доступна всем
    if 'simply' not in available_games_list:
        available_games_list.append('simply')
    
    return {
        'available_games_list': json.dumps(available_games_list)
    }
