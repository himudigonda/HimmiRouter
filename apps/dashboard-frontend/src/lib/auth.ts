import { DefaultService as ControlService } from "../client-control"

export class AuthService {
  private static AUTH_KEY = "himmi_user"

  static async register(email: string, password: string) {
    const user = await ControlService.registerAuthRegisterPost({ email, password })
    this.setSession(user)
    return user
  }

  static async login(email: string, password: string) {
    const user = await ControlService.loginAuthLoginPost({ email, password })
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

  static async getUserStatus() {
    const user = this.getSession()
    if (!user) return null
    return await ControlService.getUserStatusUsersUserIdGet(user.id)
  }

  static logout() {
    localStorage.removeItem(this.AUTH_KEY)
  }
}
