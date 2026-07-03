export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public method: string,
    public url: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      statusCode: this.statusCode,
      method: this.method,
      url: this.url,
      timestamp: new Date().toISOString(),
    };
  }
}
