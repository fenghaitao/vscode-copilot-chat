// Utility functions for the application

export function formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
}

export function validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

export class Logger {
    private context: string;
    
    constructor(context: string) {
        this.context = context;
    }
    
    info(message: string): void {
        console.log(`[${this.context}] INFO: ${message}`);
    }
    
    error(message: string): void {
        console.error(`[${this.context}] ERROR: ${message}`);
    }
}
