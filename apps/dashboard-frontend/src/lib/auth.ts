import { DefaultService as ControlService } from "../client-control"

export class AuthService {
  private static AUTH_KEY = "himmi_user"

  static async register(email: string, password: string) {
    const user = await ControlService.registerAuthRegisterPost(email, password)
    
    // Auto-login after registration
    this.setSession(user)
    return user
  }

  static setSession(user: any) {
    localStorage.setItem(this.AUTH_KEY, JSON.stringify(user))
  }

  static getSession() {
    const session = localStorage.getItem(this.AUTH_KEY)
    return session ? JSON.parse(session) : null
  }

  static logout() {
    localStorage.removeItem(this.AUTH_KEY)
  }
}
