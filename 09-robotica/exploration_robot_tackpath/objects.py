import pygame
from config import *
from memory import RouteMemory

class Car:
    """Classe que representa o carro controlado por IA."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 90, 50)
        self.speed = 4
        self.vertical_speed = 3
        self.color = BLUE
        self.state = "DRIVING"
        self.hit_timer = 0
        self.reverse_distance = 0
        self.track_top = TRACK_TOP
        self.track_bottom = TRACK_BOTTOM
        self.rect.y = max(self.track_top, min(y, self.track_bottom - self.rect.height))
        self.lane_y = self.rect.y
        self.target_y = self.rect.y
        self.original_y = self.rect.y
        self.current_obstacle = None
        self.tried_directions = set()
        self.total_reverse = 0
        self.max_reverse_distance = 200
        self.avoid_multiplier = 1
        self.max_avoid_multiplier = 10
        self.memory = RouteMemory()

    # ======================================================================
    # Métodos auxiliares
    # ======================================================================
    def _set_y(self, y):
        self.rect.y = max(self.track_top, min(y, self.track_bottom - self.rect.height))

    def _clamp_y(self):
        self._set_y(self.rect.y)

    def _is_valid_position(self, rect, obstacles, ignore_obstacle=None):
        if rect.top < self.track_top or rect.bottom > self.track_bottom:
            return False
        for obstacle in obstacles:
            if obstacle is ignore_obstacle:
                continue
            if rect.colliderect(obstacle.rect):
                return False
        return True

    def _try_move(self, dx, dy, obstacles, ignore_obstacle=None):
        new_rect = self.rect.move(dx, dy)
        if self._is_valid_position(new_rect, obstacles, ignore_obstacle):
            self.rect = new_rect
            return True
        return False

    # ======================================================================
    # Atualização principal
    # ======================================================================
    def update(self, obstacles, end_x):
        # Se chegou ao final da pista, salva a última rota pendente
        if self.rect.x >= end_x:
            if self.current_obstacle:
                offset = self.target_y - self.original_y
                self.memory.save_point(
                    self.current_obstacle.rect.x,
                    offset
                )

                self.current_obstacle = None
                self.tried_directions.clear()
                self.total_reverse = 0

            return

        # Verifica se já ultrapassou o obstáculo atual
        if self.current_obstacle:
            if self.rect.left > self.current_obstacle.rect.right:
                self.current_obstacle = None
                self.tried_directions.clear()
                self.total_reverse = 0

        # Máquina de estados
        if self.state == "HIT":
            self._handle_hit()

        elif self.state == "REVERSE":
            self._handle_reverse(obstacles)

        elif self.state == "AVOID":
            self._handle_avoid(obstacles)

        elif self.state == "RETURN":
            self._handle_return()

        else:
            self._handle_driving(obstacles)

    # ======================================================================
    # Estados
    # ======================================================================

    def _handle_hit(self):
        """Após colisão inicia a ré novamente."""
        self.hit_timer -= 1

        if self.hit_timer <= 0:
            self.state = "REVERSE"
            # sempre reinicia a ré para cada batida
            self.reverse_hit_distance = 10
            
    def _reset_avoid_multipliers(self):
        self.avoid_multiplier_up = 1
        self.avoid_multiplier_down = 1
        self.tried_directions.clear()

    def _handle_reverse(self, obstacles):
        # Fase 2 – Recuou após bater: testa desvios SEM ignorar o obstáculo atual

        # =========================
        # RÉ REALISTA APÓS BATIDA
        # =========================

        if not hasattr(self, "reverse_hit_distance"):
            self.reverse_hit_distance = 30

        # ainda precisa dar ré
        if self.reverse_hit_distance > 0:

            # velocidade da ré
            reverse_speed = 2

            # recua no eixo X
            move = -reverse_speed if self.speed > 0 else reverse_speed

            self.rect.x += move

            self.reverse_hit_distance -= abs(move)

            # continua recuando
            return


        # =========================
        # JÁ RECUOU - PROCURA DESVIO
        # =========================

        base_y = self.rect.y


        if not hasattr(self, "avoid_multiplier_up"):
            self.avoid_multiplier_up = 1

        if not hasattr(self, "avoid_multiplier_down"):
            self.avoid_multiplier_down = 1


        # =========================
        # TENTATIVA PARA CIMA
        # =========================

        desvio_up = self.rect.height * self.avoid_multiplier_up

        y_up = base_y - desvio_up

        if y_up >= self.track_top:

            teste = self.rect.copy()
            teste.y = y_up

            if self._is_valid_position(teste, obstacles, ignore_obstacle=None):

                self.target_y = y_up
                self.state = "AVOID"

                self.total_reverse = 0
                self.tried_directions.clear()

                self.avoid_multiplier_up = 1

                return


        # falhou para cima
        self.avoid_multiplier_up += 1


        # =========================
        # TENTATIVA PARA BAIXO
        # =========================

        desvio_down = self.rect.height * self.avoid_multiplier_down

        y_down = base_y + desvio_down

        if y_down + self.rect.height <= self.track_bottom:

            teste = self.rect.copy()
            teste.y = y_down

            if self._is_valid_position(teste, obstacles, ignore_obstacle=None):

                self.target_y = y_down
                self.state = "AVOID"

                self.total_reverse = 0
                self.tried_directions.clear()

                self.avoid_multiplier_down = 1

                return


        # falhou para baixo
        self.avoid_multiplier_down += 1
    
    def _handle_avoid(self, obstacles):
        """Desvia verticalmente e avança horizontalmente (com validação de colisão vertical)."""
        # Verifica se já atingiu a posição alvo
        if abs(self.rect.y - self.target_y) > self.vertical_speed:
            # Calcula o movimento vertical necessário
            if self.rect.y < self.target_y:
                dy = min(self.vertical_speed, self.target_y - self.rect.y)
            else:
                dy = max(-self.vertical_speed, self.target_y - self.rect.y)

            # Tenta mover verticalmente com validação de colisão
            if self._try_move(0, dy, obstacles):
                # Movimento vertical bem sucedido
                pass
            else:
                # Não foi possível mover verticalmente sem colidir com outro obstáculo
                self.color = RED
                self.state = "HIT"
                self.hit_timer = 20
                # Encontra qual obstáculo causou a colisão (para referência)
                for obs in obstacles:
                    if self.rect.move(0, dy).colliderect(obs.rect):
                        self.current_obstacle = obs
                        break
                return
            # Continua no próximo frame
            return

        # Atingiu a posição alvo verticalmente
        self._set_y(self.target_y)
        self._clamp_y()

        # Tenta avançar horizontalmente
        if self._try_move(self.speed, 0, obstacles):
            # Conseguiu avançar
            if self.current_obstacle:
                if self.rect.left > self.current_obstacle.rect.right:
                    # Ultrapassou o obstáculo atual: salva rota
                    offset = self.target_y - self.original_y
                    self.memory.save_point(self.current_obstacle.rect.x, offset)
                    
                    self.current_obstacle = None
                    self.tried_directions.clear()
                    self.lane_y = self.target_y
                    self.avoid_multiplier_up = 1
                    self.avoid_multiplier_down = 1
                    self.state = "DRIVING"
            else:
                # Não havia obstáculo atual, volta a dirigir
                self.state = "DRIVING"
        else:
            # Não conseguiu avançar horizontalmente: colidiu
            self.color = RED
            self.state = "HIT"
            self.hit_timer = 20
            for obs in obstacles:
                if self.rect.move(self.speed, 0).colliderect(obs.rect):
                    self.current_obstacle = obs
                    break

    def _handle_return(self):
        """Estado de retorno (não usado ativamente)."""
        self.rect.x += self.speed
        if self.rect.y < self.original_y:
            self._set_y(self.rect.y + self.vertical_speed)
        elif self.rect.y > self.original_y:
            self._set_y(self.rect.y - self.vertical_speed)
        self._clamp_y()
        if abs(self.rect.y - self.original_y) <= self.vertical_speed:
            self.rect.y = self.original_y
            self._clamp_y()
            self.state = "DRIVING"

    def _handle_driving(self, obstacles):
        """Estado normal: avança horizontalmente."""
        self._clamp_y()
        next_rect = self.rect.move(self.speed, 0)
        for obstacle in obstacles:
            if next_rect.colliderect(obstacle.rect):
                # Procura rota na memória para este obstáculo
                memory = self.memory.find_route(obstacle.rect.x)
                if memory:
                    # Calcula a posição alvo a partir da memória
                    target_y = self.original_y + memory["offset"]
                    # Valida se essa posição é segura (não colide com nenhum obstáculo)
                    test_rect = self.rect.copy()
                    test_rect.y = target_y
                    # Ignora o obstáculo atual para não bloquear a verificação
                    if self._is_valid_position(test_rect, obstacles, ignore_obstacle=obstacle):
                        # Posição segura: usa a rota
                        self.current_obstacle = obstacle
                        self.target_y = target_y
                        self.state = "AVOID"
                        return
                    else:
                        # A rota memorizada não é mais segura, então ignora e comporta como se não tivesse memória
                        # (cai no comportamento antigo de bater)
                        pass
                
                # Comportamento antigo: bater e iniciar ré
                self.state = "HIT"
                self.hit_timer = 20
                self.current_obstacle = obstacle
                return
        # Nenhum obstáculo à frente: segue em frente
        self.rect = next_rect
        self.color = BLUE

    # ======================================================================
    # Desenho (inalterado)
    # ======================================================================
    def draw(self, screen):
        x = self.rect.x
        y = self.rect.y
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (180, 220, 255), (x + 20, y + 8, 50, 18), border_radius=4)
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