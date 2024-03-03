<h1>Суть проекта:</h1>
<div>"Alien Space Wars" - это захватывающая аркадная игра,
в которой игрок управляет космическим кораблём в битве против инопланетных захватчиков.
В игре есть 6 видов врагов с разными характеристиками и 1 босс.
Во время битвы игрок может подбирать различные усилители: сердце - добавляет жизнь,
щит - добавляет единицу брони, молния - даёт игроку 15 тройных выстрелов.
Игрок управляется стрелочками на клавиатуре (движение вправо-влево), 
для стрельбы используется пробел. Одно попадание пули в персонажа вычитает одну его жизнь
или единицу брони (если она имеется).
При попадании в персонажа его картинка на 30 миллисекунд становиться светлее,
затем возвращается в прежнее состояние (таким образом визуализируется попадание).</div>
<h1>Особенности кода программы:</h1>
<div>Каждый персонаж и предмет в игре написан собственным классом,
унаследованным от класса pygame.sprite.Sprite.
Каждый спрайт занесен в общую группу all_sprites (используется для отрисовки),
а также в собственную группу.
Update() каждой собственной группы выполняется отдельно для этой группы
из-за особенностей передаваемых параметров в эту функцию.</div>
<div>В игре присутствует 3 основных экрана. За каждый экран отвечает своя функция: 
main() - непосредственно сама игра, start_screen() - экран заставки с кнопкой "play", 
game_over() - экран с надписью "GAME OVER" и кнопкой для выхода.
В каждой из этих функций есть свой игровой цикл, отрисовывающий экран.
Для выхода из pygame используется функция terminate().</div>