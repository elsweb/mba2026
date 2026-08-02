import pygame
from config import *

class Car:
    """Classe que representa o carro controlado por IA."""

    def __init__(self, x, y):
        # Retângulo do carro (largura 90, altura 50)
        self.rect = pygame.Rect(x, y, 90, 50)

        # Velocidades
        self.speed = 4
        self.vertical_speed = 3

        self.color = BLUE

        # Estados possíveis: DRIVING, HIT, REVERSE, AVOID, RETURN
        self.state = "DRIVING"

        # Temporizador após colisão
        self.hit_timer = 0
        self.reverse_distance = 0

        # Limites da pista (valores fixos, poderiam vir do config)
        self.track_top = TRACK_TOP
        self.track_bottom = TRACK_BOTTOM

        # Garante que a posição inicial esteja dentro dos limites
        self.rect.y = max(self.track_top, min(y, self.track_bottom - self.rect.height))
        self.lane_y = self.rect.y
        self.target_y = self.rect.y
        self.original_y = self.rect.y

        # Memória do obstáculo atual e direções já tentadas
        self.current_obstacle = None
        self.tried_directions = set()

    # ======================================================================
    # Métodos auxiliares para manter o carro dentro da pista e validar posição
    # ======================================================================

    def _set_y(self, y):
        """Define a posição Y mantendo o carro dentro da pista."""
        self.rect.y = max(
            self.track_top,
            min(y, self.track_bottom - self.rect.height)
        )

    def _clamp_y(self):
        """Apenas chama _set_y com a posição atual (garante limites)."""
        self._set_y(self.rect.y)

    def _is_valid_position(self, rect, obstacles, ignore_obstacle=None):
        """
        Verifica se a posição é válida:
        - Dentro da pista
        - Sem bater em obstáculos (exceto ignore_obstacle)
        """
        # Limite superior
        if rect.top < self.track_top:
            return False
        # Limite inferior
        if rect.bottom > self.track_bottom:
            return False
        # Colisão com obstáculos
        for obstacle in obstacles:
            if obstacle is ignore_obstacle:
                continue
            if rect.colliderect(obstacle.rect):
                return False
        return True

    def _try_move(self, dx, dy, obstacles, ignore_obstacle=None):
        """
        Tenta mover o carro de (dx, dy). Se a nova posição for válida,
        aplica o movimento e retorna True. Caso contrário, retorna False.
        ignore_obstacle: opcional, obstáculo a ser ignorado na colisão
                         (útil para não colidir com o mesmo obstáculo ao recuar).
        """
        new_rect = self.rect.move(dx, dy)
        if self._is_valid_position(new_rect, obstacles, ignore_obstacle):
            self.rect = new_rect
            return True
        return False

    # ======================================================================
    # Atualização principal
    # ======================================================================

    def update(self, obstacles, end_x):
        """
        Atualiza o estado do carro a cada frame.
        obstacles: lista de Obstacle
        end_x: posição X da linha de chegada (se atingida, para de andar)
        """
        # Se já passou da linha de chegada, não faz nada
        if self.rect.x >= end_x:
            return

        # Limpa memória se já ultrapassou o obstáculo atual
        if self.current_obstacle:
            if self.rect.left > self.current_obstacle.rect.right:
                self.current_obstacle = None
                self.tried_directions.clear()

        # Chama o método correspondente ao estado atual
        if self.state == "HIT":
            self._handle_hit()
        elif self.state == "REVERSE":
            self._handle_reverse(obstacles)
        elif self.state == "AVOID":
            self._handle_avoid(obstacles)
        elif self.state == "RETURN":
            self._handle_return(obstacles)
        else:  # DRIVING
            self._handle_driving(obstacles)

    # ======================================================================
    # Estados
    # ======================================================================

    def _handle_hit(self):
        """Estado após colisão: espera um tempo antes de dar ré."""
        self.hit_timer -= 1
        if self.hit_timer <= 0:
            self.state = "REVERSE"
            self.reverse_distance = 30

    def _handle_reverse(self, obstacles):
        """Recua e tenta encontrar uma nova faixa livre."""
        # Recua, ignorando o obstáculo atual para não ficar preso
        if self._try_move(-2, 0, obstacles, ignore_obstacle=self.current_obstacle):
            self.reverse_distance -= 2
        # Se não conseguir recuar, mantém a distância e tenta novamente no próximo frame

        if self.reverse_distance <= 0:
            # Calcula o espaço máximo disponível para cima e para baixo
            max_up = self.rect.top - self.track_top
            max_down = self.track_bottom - self.rect.bottom

            # Lista de tentativas (apenas as que cabem)
            tentativas = []
            DESVIO = 40
            if max_up >= DESVIO:
                tentativas.append(("UP", -DESVIO))
            if max_down >= DESVIO:
                tentativas.append(("DOWN", DESVIO))

            escolhido = None
            for direcao, offset in tentativas:
                if direcao in self.tried_directions:
                    continue
                teste = self.rect.copy()
                teste.y = max(
                    self.track_top,
                    min(teste.y + offset, self.track_bottom - teste.height)
                )
                # Verifica se a posição é válida (ignorando o obstáculo atual para permitir desvio)
                if self._is_valid_position(teste, obstacles, ignore_obstacle=self.current_obstacle):
                    escolhido = (direcao, teste.y)
                    break

            if escolhido:
                direcao, novo_y = escolhido
                # Garantia extra (já foi validado, mas por segurança)
                novo_y = max(self.track_top, min(novo_y, self.track_bottom - self.rect.height))
                self.target_y = novo_y
                self.tried_directions.add(direcao)
                self.state = "AVOID"
            else:
                # Não achou espaço, continua recuando
                self.reverse_distance = 40

    def _handle_avoid(self, obstacles):
        """
        Estado de desvio: move-se verticalmente até a target_y e,
        em seguida, avança até ultrapassar o obstáculo.
        """
        # Movimento vertical em direção ao alvo (ignora o obstáculo atual para não travar)
        if abs(self.rect.y - self.target_y) > self.vertical_speed:
            dy = self.vertical_speed if self.rect.y < self.target_y else -self.vertical_speed
            # Tenta mover verticalmente, ignorando o obstáculo que motivou o desvio
            if not self._try_move(0, dy, obstacles, ignore_obstacle=self.current_obstacle):
                # Se não consegue mover, mantém a posição e tenta novamente no próximo frame
                pass
            return

        # Chegou na faixa alvo
        self._set_y(self.target_y)
        self._clamp_y()

        # Avança horizontalmente, verificando colisão com TODOS os obstáculos
        if self._try_move(self.speed, 0, obstacles):
            # Verifica se já passou completamente do obstáculo que motivou o desvio
            if self.current_obstacle and self.rect.left > self.current_obstacle.rect.right:
                self.current_obstacle = None
                self.tried_directions.clear()
                self.lane_y = self.target_y
                self.state = "DRIVING"
        else:
            # Bateu em outro obstáculo (ou no mesmo) durante o avanço → volta para HIT
            self.color = RED
            self.state = "HIT"
            self.hit_timer = 20
            # Atualiza o obstáculo atual para o que causou a colisão
            for obs in obstacles:
                if self.rect.move(self.speed, 0).colliderect(obs.rect):
                    self.current_obstacle = obs
                    break

    def _handle_return(self, obstacles):
        """
        Estado de retorno à faixa original (não usado ativamente,
        mas mantido para possível extensão).
        """
        # Avança horizontalmente (com validação)
        if not self._try_move(self.speed, 0, obstacles):
            # Se não conseguir avançar, pode ficar preso; melhor entrar em HIT
            self.state = "HIT"
            self.hit_timer = 20
            return

        # Move verticalmente em direção à faixa original (com validação)
        if self.rect.y < self.original_y:
            dy = self.vertical_speed
        elif self.rect.y > self.original_y:
            dy = -self.vertical_speed
        else:
            dy = 0

        if dy != 0:
            if not self._try_move(0, dy, obstacles):
                # Se não conseguir mover verticalmente, mantém a posição
                pass

        # Se chegou próximo o suficiente, trava na faixa original
        if abs(self.rect.y - self.original_y) <= self.vertical_speed:
            self.rect.y = self.original_y
            self._clamp_y()
            self.state = "DRIVING"

    def _handle_driving(self, obstacles):
        """
        Estado normal: tenta avançar; se colidir com algum obstáculo,
        entra no estado HIT.
        """
        # Segurança: garante que o carro está dentro da pista
        self._clamp_y()

        # Tenta mover para frente
        if self._try_move(self.speed, 0, obstacles):
            self.color = BLUE
        else:
            # Colidiu → entra em HIT
            self.color = RED
            # Descobre qual obstáculo causou a colisão
            for obs in obstacles:
                if self.rect.move(self.speed, 0).colliderect(obs.rect):
                    self.current_obstacle = obs
                    break
            self.state = "HIT"
            self.hit_timer = 20

    # ======================================================================
    # Desenho do carro na tela
    # ======================================================================

    def draw(self, screen):
        """Desenha o carro com detalhes (faróis, rodas, etc.)."""
        x = self.rect.x
        y = self.rect.y

        # Carroceria principal
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=10
        )

        # Para-brisa
        pygame.draw.rect(
            screen,
            (180, 220, 255),
            (x + 20, y + 8, 50, 18),
            border_radius=4
        )

        # Rodas
        pygame.draw.circle(screen, BLACK, (x + 18, y + 5), 8)
        pygame.draw.circle(screen, BLACK, (x + 72, y + 5), 8)
        pygame.draw.circle(screen, BLACK, (x + 18, y + 45), 8)
        pygame.draw.circle(screen, BLACK, (x + 72, y + 45), 8)


class Obstacle:
    """Classe para obstáculos estáticos na pista."""

    def __init__(self, x, y, w=40, h=40, color=(255, 100, 0)):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self, screen):
        """Desenha o obstáculo como um retângulo arredondado."""
        pygame.draw.rect(
            screen,
            self.color,
            self.rect,
            border_radius=5
        )