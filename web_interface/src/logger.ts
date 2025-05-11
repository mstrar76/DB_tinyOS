/**
 * Serviço de logging estruturado em formato JSON para a interface web
 * Este sistema de logs permite o rastreamento fácil de requisições e erros
 */

// Enumeração dos níveis de log disponíveis
enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

// Interface que define a estrutura do log
interface LogEntry {
  timestamp: string;
  level: LogLevel;
  service: string;
  message: string;
  correlationId?: string;
  data?: any;
}

// Classe responsável pelo logging estruturado
class Logger {
  private serviceName: string;
  private correlationId?: string;

  constructor(serviceName: string, correlationId?: string) {
    this.serviceName = serviceName;
    this.correlationId = correlationId || this.generateCorrelationId();
  }

  // Gera um ID de correlação para rastrear requisições entre serviços
  private generateCorrelationId(): string {
    return `web-${Date.now()}-${Math.random().toString(36).substring(2, 10)}`;
  }

  // Cria uma entrada de log estruturada
  private createLogEntry(level: LogLevel, message: string, data?: any): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      service: this.serviceName,
      message,
      correlationId: this.correlationId,
      data,
    };
  }

  // Formata e envia o log para o console
  private log(level: LogLevel, message: string, data?: any): void {
    const entry = this.createLogEntry(level, message, data);
    const logJson = JSON.stringify(entry);

    // Envia para o console com a formatação adequada para o nível
    switch (level) {
      case LogLevel.DEBUG:
        console.debug(logJson);
        break;
      case LogLevel.INFO:
        console.info(logJson);
        break;
      case LogLevel.WARN:
        console.warn(logJson);
        break;
      case LogLevel.ERROR:
        console.error(logJson);
        break;
    }

    // Aqui poderia ser adicionado código para enviar logs para um sistema centralizado
    // Por exemplo, enviar para um endpoint backend que armazene os logs
  }

  // Métodos públicos de logging
  debug(message: string, data?: any): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  info(message: string, data?: any): void {
    this.log(LogLevel.INFO, message, data);
  }

  warn(message: string, data?: any): void {
    this.log(LogLevel.WARN, message, data);
  }

  error(message: string, data?: any): void {
    this.log(LogLevel.ERROR, message, data);
  }
}

// Exporta uma instância singleton do logger para ser usada em toda a aplicação
export const logger = new Logger('web-interface');

// Exporta a classe e interfaces para permitir extensões
export { Logger, LogLevel, LogEntry };
