from .models import ClassGameAccess

def available_games(request):
    """
    Контекстный процессор для определения доступных игр
    """
    available_games_list = []
    
    # Если это ученик (авторизован через сессию)
    if request.session.get('student_id'):
        try:
            from .models import Students
            student = Students.objects.get(id=request.session['student_id'])
            if student.student_class:
                # Получаем игры, доступные для класса ученика
                class_games = ClassGameAccess.objects.filter(
                    class_group=student.student_class,
                    is_enabled=True
                )
                available_games_list = [game.game for game in class_games]
        except:
            pass
    
    # Если это учитель (авторизован через Django)
    elif hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.status == 'approved':
        # Учитель имеет доступ ко всем играм
        available_games_list = [
            'multiplication_choose',
            'multiplication_to_20', 
            'square',
            'tricks',
            'flashcards',
            'multiplication_base'
        ]
    
    # Игра "simply" всегда доступна всем
    if 'simply' not in available_games_list:
        available_games_list.append('simply')
    
    return {
        'available_games_list': available_games_list
    }
