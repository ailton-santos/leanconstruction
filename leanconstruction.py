import random

class Task:
    """
    Representa uma atividade do projeto de construção.
    
    Attributes:
      name: Nome da atividade.
      base_duration: Duração base da atividade (dias).
      value_added: Indica se a atividade agrega valor.
      delay_factor: Atraso máximo possível (dias) em atividades que não agregam valor.
      delay_probability: Probabilidade de ocorrer atraso.
      dependencies: Lista de nomes de atividades que devem ser concluídas antes.
    """
    def __init__(self, name, base_duration, value_added, delay_factor=0, delay_probability=1.0, dependencies=None):
        self.name = name
        self.base_duration = base_duration
        self.value_added = value_added
        self.delay_factor = delay_factor
        self.delay_probability = delay_probability
        self.dependencies = dependencies if dependencies else []
        
    def simulate_duration(self):
        """Simula a duração efetiva da atividade, incluindo atraso se aplicável."""
        delay = 0
        if not self.value_added and self.delay_factor > 0:
            if random.random() < self.delay_probability:
                delay = random.uniform(0, self.delay_factor)
        return self.base_duration + delay

def simulate_project(return_schedule=False, lean_improvement=0):
    """
    Simula o cronograma de um projeto de construção.
    
    Parâmetros:
      lean_improvement: Valor entre 0 e 1 que reduz o atraso em atividades não-valor agregado.
                        0 significa sem melhoria e 1 elimina os atrasos.
      return_schedule: Se True, retorna o cronograma detalhado.
    
    Retorna:
      - Se return_schedule for True:
          schedule: Dicionário com (início, término, duração real, se agrega valor, duração base) para cada tarefa.
          total_duration: Duração total do projeto (dias).
          total_value_added: Soma das durações base das atividades que agregam valor.
          efficiency: Eficiência do projeto (valor agregado / duração total * 100).
      - Caso contrário, retorna (total_duration, total_value_added, efficiency).
    """
    # Definição das atividades do projeto
    tasks = [
        Task("Planejamento", 20, True, dependencies=[]),
        Task("Licenciamento", 10, False, delay_factor=5 * (1 - lean_improvement), delay_probability=0.8, dependencies=["Planejamento"]),
        Task("Mobilização", 5, False, delay_factor=3 * (1 - lean_improvement), delay_probability=0.7, dependencies=["Licenciamento"]),
        Task("Escavação", 15, True, dependencies=["Mobilização"]),
        Task("Estrutura", 25, True, dependencies=["Escavação"]),
        Task("Alvenaria", 20, True, dependencies=["Estrutura"]),
        Task("Instalações", 10, True, dependencies=["Estrutura"]),
        Task("Acabamentos", 10, True, dependencies=["Alvenaria", "Instalações"]),
        Task("Inspeção", 5, True, dependencies=["Acabamentos"])
    ]
    
    # Cria um dicionário para acesso rápido por nome
    tasks_by_name = {task.name: task for task in tasks}
    
    # Ordenação topológica das tarefas (garante que as dependências sejam processadas primeiro)
    order = []
    seen = set()
    def visit(task):
        for dep in task.dependencies:
            if dep not in seen:
                visit(tasks_by_name[dep])
        if task.name not in seen:
            seen.add(task.name)
            order.append(task)
    for task in tasks:
        visit(task)
        
    # Calcula o cronograma: para cada tarefa, determina o início (máximo dos términos das dependências)
    # e o término (início + duração simulada)
    schedule = {}  # {nome: (start, finish, real_duration, value_added, base_duration)}
    for task in order:
        if task.dependencies:
            start_time = max(schedule[dep][1] for dep in task.dependencies)
        else:
            start_time = 0
        duration = task.simulate_duration()
        finish_time = start_time + duration
        schedule[task.name] = (start_time, finish_time, duration, task.value_added, task.base_duration)
        
    total_duration = schedule["Inspeção"][1] if "Inspeção" in schedule else max(entry[1] for entry in schedule.values())
    total_value_added = sum(task.base_duration for task in tasks if task.value_added)
    efficiency = 100 * (total_value_added / total_duration)
    
    if return_schedule:
        return schedule, total_duration, total_value_added, efficiency
    else:
        return total_duration, total_value_added, efficiency

def print_schedule(schedule):
    """Exibe o cronograma detalhado do projeto."""
    print("Cronograma Detalhado do Projeto:")
    print(f"{'Atividade':20s} {'Início (dias)':15s} {'Término (dias)':15s} {'Duração Real (dias)':20s} {'Duração Base':15s} {'Valor Agregado':15s}")
    for task, data in schedule.items():
        start, finish, real_duration, value_added, base = data
        va_str = "Sim" if value_added else "Não"
        print(f"{task:20s} {start:15.2f} {finish:15.2f} {real_duration:20.2f} {base:15.2f} {va_str:15s}")

def run_detailed_simulation():
    """Executa uma simulação única e exibe o cronograma detalhado."""
    schedule, total_duration, total_value_added, efficiency = simulate_project(return_schedule=True)
    print_schedule(schedule)
    print("\nResumo do Projeto:")
    print(f"Duração total do projeto: {total_duration:.2f} dias")
    print(f"Tempo total das atividades com valor agregado: {total_value_added:.2f} dias")
    print(f"Eficiência (valor agregado / duração total): {efficiency:.2f}%")
    
def run_monte_carlo_simulation(num_simulations=1000, lean_improvement=0):
    """
    Executa uma simulação Monte Carlo para estimar estatísticas do projeto.
    
    Parâmetros:
      num_simulations: Número de simulações a serem executadas.
      lean_improvement: Fator de melhoria Lean (0 a 1) para reduzir atrasos.
    """
    total_duration = 0
    total_value_added = 0
    durations = []
    for _ in range(num_simulations):
        dur, val, _ = simulate_project(lean_improvement=lean_improvement)
        total_duration += dur
        total_value_added += val
        durations.append(dur)
    avg_duration = total_duration / num_simulations
    avg_value_added = total_value_added / num_simulations
    efficiency = 100 * (avg_value_added / avg_duration)
    print("Simulação Monte Carlo Lean Construction")
    print(f"Número de simulações: {num_simulations}")
    print(f"Duração média do projeto: {avg_duration:.2f} dias")
    print(f"Tempo médio das atividades com valor agregado: {avg_value_added:.2f} dias")
    print(f"Eficiência (valor agregado / duração total): {efficiency:.2f}%")
    print(f"Duração mínima: {min(durations):.2f} dias")
    print(f"Duração máxima: {max(durations):.2f} dias")
    
def main():
    print("Simulação Lean Construction Detalhada")
    print("Escolha a opção:")
    print("1 - Simulação Detalhada (cronograma único)")
    print("2 - Simulação Monte Carlo")
    choice = input("Digite 1 ou 2: ")
    if choice == "1":
        run_detailed_simulation()
    elif choice == "2":
        num_sim = input("Número de simulações (padrão 1000): ")
        try:
            num_sim = int(num_sim)
        except:
            num_sim = 1000
        improvement = input("Fator de melhoria Lean (0 a 1, onde 0 = sem melhoria e 1 = sem atrasos): ")
        try:
            improvement = float(improvement)
            if improvement < 0 or improvement > 1:
                improvement = 0
        except:
            improvement = 0
        run_monte_carlo_simulation(num_sim, lean_improvement=improvement)
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
