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

        # Faixa atual (posição Y alvo)
        self.lane_y = y
        self.target_y = y

        # Limites da pista (valores fixos, poderiam vir do config)
        self.track_top = 100
        self.track_bottom = 600

        # Memória do obstáculo atual e direções já tentadas
        self.current_obstacle = None
        self.tried_directions = set()

        # Guarda a posição original para o estado RETURN (se usado)
        self.original_y = y

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
            self._handle_return()
        else:  # DRIVING
            self._handle_driving(obstacles)

    # ======================================================================
    # Métodos auxiliares para cada estado
    # ======================================================================

    def _handle_hit(self):
        """Estado após colisão: espera um tempo antes de dar ré."""
        self.hit_timer -= 1
        if self.hit_timer <= 0:
            self.state = "REVERSE"
            self.reverse_distance = 30

    def _handle_reverse(self, obstacles):
        """
        Estado de ré: recua um pouco e tenta encontrar uma direção livre
        (para cima ou para baixo) que ainda não foi tentada.
        """
        self.rect.x -= 2
        self.reverse_distance -= 2

        if self.reverse_distance <= 0:
            offset = 60
            caminhos = []

            # Verifica direção para cima
            if "UP" not in self.tried_directions:
                if self.rect.y - offset >= self.track_top:
                    caminhos.append(("UP", self.rect.y - offset))

            # Verifica direção para baixo
            if "DOWN" not in self.tried_directions:
                if self.rect.y + offset + self.rect.height <= self.track_bottom:
                    caminhos.append(("DOWN", self.rect.y + offset))

            escolhido = None
            for direcao, y in caminhos:
                teste = self.rect.copy()
                teste.y = y
                # Verifica se a nova posição não colide com nenhum obstáculo
                if not any(teste.colliderect(o.rect) for o in obstacles):
                    escolhido = (direcao, y)
                    break

            if escolhido:
                direcao, y = escolhido
                self.target_y = y
                self.tried_directions.add(direcao)
                self.state = "AVOID"
            else:
                # Nenhuma direção livre: continua ré e tentará de novo
                self.reverse_distance = 30

    def _handle_avoid(self, obstacles):
        """
        Estado de desvio: move-se verticalmente até a target_y e,
        em seguida, avança até ultrapassar o obstáculo.
        """
        # Move verticalmente em direção ao alvo
        if abs(self.rect.y - self.target_y) > self.vertical_speed:
            if self.rect.y < self.target_y:
                self.rect.y += self.vertical_speed
            else:
                self.rect.y -= self.vertical_speed
            return  # continua no próximo frame

        # Chegou na faixa alvo
        self.rect.y = self.target_y

        # Avança horizontalmente
        self.rect.x += self.speed

        # Verifica se já passou completamente do obstáculo
        if self.current_obstacle:
            if self.rect.left > self.current_obstacle.rect.right:
                self.current_obstacle = None
                self.tried_directions.clear()
                self.lane_y = self.target_y
                self.state = "DRIVING"
        else:
            # Caso não tenha obstáculo memorizado (segurança)
            self.state = "DRIVING"

    def _handle_return(self):
        """
        Estado de retorno à faixa original (não usado ativamente,
        mas mantido para possível extensão).
        """
        self.rect.x += self.speed

        if self.rect.y < self.original_y:
            self.rect.y += self.vertical_speed
        elif self.rect.y > self.original_y:
            self.rect.y -= self.vertical_speed

        if abs(self.rect.y - self.original_y) <= self.vertical_speed:
            self.rect.y = self.original_y
            self.state = "DRIVING"

    def _handle_driving(self, obstacles):
        """
        Estado normal: tenta avançar; se colidir com algum obstáculo,
        entra no estado HIT.
        """
        next_rect = self.rect.move(self.speed, 0)

        for obstacle in obstacles:
            if next_rect.colliderect(obstacle.rect):
                self.color = RED

                if self.current_obstacle != obstacle:
                    self.current_obstacle = obstacle
                    self.tried_directions.clear()

                self.state = "HIT"
                self.hit_timer = 20
                return

        # Caminho livre
        self.rect = next_rect
        self.color = BLUE

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